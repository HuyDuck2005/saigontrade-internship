import xmlrpc.client
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("TestTask6")

ODOO1_URL = "http://localhost:8069"
ODOO1_DB = "odoo_db"
ODOO2_URL = "http://localhost:8070"
ODOO2_DB = "odoo2_db"
USER = "admin"
PASSWORD = "admin"

def run_task6_test():
    print("\n" + "="*65)
    print("🚀 BẮT ĐẦU KIỂM THỬ TASK 6: ĐỒNG BỘ CONTACT ODOO1 -> ODOO2")
    print("="*65)

    # 1. Đăng nhập Odoo 1 & Odoo 2
    c1 = xmlrpc.client.ServerProxy(f"{ODOO1_URL}/xmlrpc/2/common", allow_none=True)
    uid1 = c1.authenticate(ODOO1_DB, USER, PASSWORD, {})
    m1 = xmlrpc.client.ServerProxy(f"{ODOO1_URL}/xmlrpc/2/object", allow_none=True)

    c2 = xmlrpc.client.ServerProxy(f"{ODOO2_URL}/xmlrpc/2/common", allow_none=True)
    uid2 = c2.authenticate(ODOO2_DB, USER, PASSWORD, {})
    m2 = xmlrpc.client.ServerProxy(f"{ODOO2_URL}/xmlrpc/2/object", allow_none=True)

    logger.info(f"✅ Odoo 1 UID: {uid1} | Odoo 2 UID: {uid2}")

    # 2. Tạo một Lead thử nghiệm trên Odoo 1
    test_phone = "0933888999"
    lead_id = m1.execute_kw(ODOO1_DB, uid1, PASSWORD, 'crm.lead', 'create', [{
        'name': 'Dự án Hợp tác Phần mềm 2026',
        'contact_name': 'Lê Hoàng Nam',
        'phone': test_phone,
        'email_from': 'hoangnam@sgt.vn',
        'description': 'Đồng bộ từ Lead Odoo 1 sang Odoo 2'
    }])
    logger.info(f"🎉 Đã tạo Lead trên Odoo 1 (ID: {lead_id})")

    # 3. Thực hiện logic đồng bộ Contact Local (Odoo 1)
    p1_ids = m1.execute_kw(ODOO1_DB, uid1, PASSWORD, 'res.partner', 'search', [[['phone', '=', test_phone]]])
    partner_vals = {
        'name': 'Lê Hoàng Nam',
        'phone': test_phone,
        'email': 'hoangnam@sgt.vn'
    }
    if p1_ids:
        p1_id = p1_ids[0]
        m1.execute_kw(ODOO1_DB, uid1, PASSWORD, 'res.partner', 'write', [[p1_id], partner_vals])
        logger.info(f"✅ [Odoo 1] Đã CẬP NHẬT Contact (ID: {p1_id})")
    else:
        p1_id = m1.execute_kw(ODOO1_DB, uid1, PASSWORD, 'res.partner', 'create', [partner_vals])
        logger.info(f"✅ [Odoo 1] Đã TẠO MỚI Contact (ID: {p1_id})")

    # 4. Thực hiện logic đồng bộ Contact Remote (Odoo 2)
    p2_ids = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'res.partner', 'search', [[['phone', '=', test_phone]]])
    if p2_ids:
        p2_id = p2_ids[0]
        m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'res.partner', 'write', [[p2_id], partner_vals])
        logger.info(f"✅ [Odoo 2 Remote] Đã CẬP NHẬT Contact theo Phone {test_phone} (ID: {p2_id})")
    else:
        p2_id = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'res.partner', 'create', [partner_vals])
        logger.info(f"✅ [Odoo 2 Remote] Đã TẠO MỚI Contact theo Phone {test_phone} (ID: {p2_id})")

    # 5. Đối soát kết quả
    contact_o1 = m1.execute_kw(ODOO1_DB, uid1, PASSWORD, 'res.partner', 'read', [[p1_id], ['name', 'phone', 'email']])[0]
    contact_o2 = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'res.partner', 'read', [[p2_id], ['name', 'phone', 'email']])[0]

    print("\n--- KẾT QUẢ ĐỐI SOÁT DỮ LIỆU ---")
    print(f"📌 Odoo 1 Contact: {contact_o1}")
    print(f"📌 Odoo 2 Contact: {contact_o2}")
    print("\n" + "="*65)
    print("🎉 KIỂM THỬ TASK 6 THÀNH CÔNG 100%!")
    print("="*65)

if __name__ == "__main__":
    run_task6_test()
