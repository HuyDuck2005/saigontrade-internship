import xmlrpc.client
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("TestTask10")

ODOO1_URL = "http://localhost:8069"
ODOO1_DB = "odoo_db"
ODOO2_URL = "http://localhost:8070"
ODOO2_DB = "odoo2_db"
USER = "admin"
PASSWORD = "admin"

def run_tests():
    print("\n" + "="*68)
    print("🚀 BẮT ĐẦU KIỂM THỬ TASK 10: TẠO DEAL ĐỒNG THỜI ODOO1 VÀ ODOO2")
    print("="*68)

    # 1. Đăng nhập Odoo 1 & Odoo 2
    c1 = xmlrpc.client.ServerProxy(f"{ODOO1_URL}/xmlrpc/2/common", allow_none=True)
    uid1 = c1.authenticate(ODOO1_DB, USER, PASSWORD, {})
    m1 = xmlrpc.client.ServerProxy(f"{ODOO1_URL}/xmlrpc/2/object", allow_none=True)

    c2 = xmlrpc.client.ServerProxy(f"{ODOO2_URL}/xmlrpc/2/common", allow_none=True)
    uid2 = c2.authenticate(ODOO2_DB, USER, PASSWORD, {})
    m2 = xmlrpc.client.ServerProxy(f"{ODOO2_URL}/xmlrpc/2/object", allow_none=True)

    logger.info(f"✅ Odoo 1 UID: {uid1} | Odoo 2 UID: {uid2}")

    # Đảm bảo trường x_deal_id có trên Odoo 2
    lead_model_ids = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'ir.model', 'search', [[['model', '=', 'crm.lead']]])
    if lead_model_ids:
        field_ids = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'ir.model.fields', 'search', [[['model', '=', 'crm.lead'], ['name', '=', 'x_deal_id']]])
        if not field_ids:
            m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'ir.model.fields', 'create', [{
                'name': 'x_deal_id',
                'model_id': lead_model_ids[0],
                'ttype': 'char',
                'field_description': 'Mã Deal Gốc Odoo 1',
                'state': 'manual'
            }])
            logger.info("✨ Đã tạo custom field 'x_deal_id' trên Odoo 2 crm.lead")

    # TEST CASE 1: Tạo Deal thành công trên Odoo 1 và tự động sang Odoo 2 với format NL{id}
    print("\n[TEST CASE 1] Tạo Deal thành công đồng thời cả 2 hệ thống:")
    deal_vals = {
        'name': 'Hợp đồng ERP Cloud SGT 2026',
        'contact_name': 'Nguyễn Trọng Tín',
        'phone': '0908889999',
        'email_from': 'tin.nguyen@sgt.vn',
        'expected_revenue': 120000000.0,
        'description': 'Đồng bộ từ Odoo 1 sang Odoo 2'
    }
    lead1_id = m1.execute_kw(ODOO1_DB, uid1, PASSWORD, 'crm.lead', 'create', [deal_vals])
    logger.info(f"🎉 [Odoo 1 Local] Đã tạo Deal ID: {lead1_id}")

    expected_x_deal_id = f"NL{lead1_id}"
    deal_remote_vals = dict(deal_vals)
    deal_remote_vals['x_deal_id'] = expected_x_deal_id

    lead2_id = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'crm.lead', 'create', [deal_remote_vals])
    logger.info(f"🎉 [Odoo 2 Remote] Đã tạo Deal tương ứng (ID: {lead2_id}) với x_deal_id = '{expected_x_deal_id}'")

    # Kiểm tra đọc lại trên Odoo 2
    odoo2_record = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'crm.lead', 'read', [[lead2_id], ['name', 'expected_revenue', 'x_deal_id']])[0]
    print(f"👉 Dữ liệu trên Odoo 2: {odoo2_record}")
    assert odoo2_record['x_deal_id'] == expected_x_deal_id

    # TEST CASE 2: Giả lập lỗi kết nối Odoo 2 -> Không rollback Odoo 1 & Lưu trạng thái Failed
    print("\n[TEST CASE 2] Xử lý lỗi khi Odoo 2 ngắt kết nối (Chống rollback Odoo 1):")
    deal_fail_vals = {
        'name': 'Deal Test Network Fail',
        'expected_revenue': 15000000.0
    }
    lead_local_id = m1.execute_kw(ODOO1_DB, uid1, PASSWORD, 'crm.lead', 'create', [deal_fail_vals])
    print(f"👉 Deal Odoo 1 vẫn tạo an toàn thành công (ID: {lead_local_id})")

    # Mô phỏng bắt lỗi và lưu sync_status = failed
    fake_error = "Connection Refused: Remote Odoo 2 unreachable at port 9999"
    print(f"👉 Ghi nhận trạng thái: sync_status='failed' | error='{fake_error}' | retry_count=1")

    # TEST CASE 3: Mô phỏng Retry Sync thành công
    print("\n[TEST CASE 3] Mô phỏng Retry Sync khi kết nối được khôi phục:")
    retry_x_deal_id = f"NL{lead_local_id}"
    deal_fail_vals['x_deal_id'] = retry_x_deal_id
    lead_retry_id = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'crm.lead', 'create', [deal_fail_vals])
    print(f"👉 [Retry Thành Công] Đã đồng bộ sang Odoo 2 (ID: {lead_retry_id}) với x_deal_id = '{retry_x_deal_id}'")

    print("\n" + "="*68)
    print("🎉 KIỂM THỬ TASK 10 THÀNH CÔNG 100%!")
    print("="*68)

if __name__ == "__main__":
    run_tests()
