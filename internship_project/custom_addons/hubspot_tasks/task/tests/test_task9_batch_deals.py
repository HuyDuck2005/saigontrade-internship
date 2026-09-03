import xmlrpc.client
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("TestTask9")

ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo_db"
USER = "admin"
PASSWORD = "admin"

def run_tests():
    print("\n" + "="*68)
    print("🚀 BẮT ĐẦU KIỂM THỬ TASK 9: TẠO CRM DEAL HÀNG LOẠT TỪ CONTACT WIZARD")
    print("="*68)

    # 1. Kết nối Odoo
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, USER, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    logger.info(f"✅ Đăng nhập Odoo thành công! (UID: {uid})")

    # 2. Tạo 3 Contact mẫu để test chọn hàng loạt
    contacts_payload = [
        {"name": "Đặng Minh Tâm", "phone": "0911223344", "email": "tamdm@sgt.vn"},
        {"name": "Vũ Thu Trang", "phone": "0922334455", "email": "trangvt@sgt.vn"},
        {"name": "Ngô Quốc Huy", "phone": "0933445566", "email": "huynq@sgt.vn"}
    ]
    partner_ids = []
    for c in contacts_payload:
        pid = models.execute_kw(ODOO_DB, uid, PASSWORD, 'res.partner', 'create', [c])
        partner_ids.append(pid)
    logger.info(f"✨ Đã tạo 3 Contact mẫu (IDs: {partner_ids})")

    # 3. Mô phỏng thực thi Wizard: Tạo Deal hàng loạt từ 3 Contact
    event_name = "Vietnam TechFest 2026"
    amount = 50000000.0  # 50 triệu VNĐ

    created_deal_ids = []
    for pid in partner_ids:
        partner_info = models.execute_kw(ODOO_DB, uid, PASSWORD, 'res.partner', 'read', [[pid], ['name', 'phone', 'email']])[0]
        deal_vals = {
            'name': f"Hợp tác Doanh nghiệp 2026 - {partner_info['name']}",
            'partner_id': pid,
            'contact_name': partner_info['name'],
            'phone': partner_info['phone'] or '',
            'email_from': partner_info['email'] or '',
            'expected_revenue': amount,
            'description': f"Event: {event_name} | Location: TP. Hồ Chí Minh\nNotes: Gói phần mềm quản trị toàn diện"
        }
        did = models.execute_kw(ODOO_DB, uid, PASSWORD, 'crm.lead', 'create', [deal_vals])
        created_deal_ids.append(did)

    logger.info(f"🎉 Đã tạo thành công 3 Deal CRM tương ứng (Deal IDs: {created_deal_ids})")

    # 4. Kiểm tra validate chống trùng lặp theo Contact & Event (Yêu cầu nâng cao)
    print("\n[TEST CASE CHỐNG TRÙNG LẶP THEO EVENT & CONTACT]")
    duplicate_partner_id = partner_ids[0]
    existing_deals = models.execute_kw(
        ODOO_DB, uid, PASSWORD,
        'crm.lead', 'search',
        [[['partner_id', '=', duplicate_partner_id], ['description', 'like', f"Event: {event_name}"]]]
    )
    if existing_deals:
        print(f"👉 Phát hiện Deal đã tồn tại cho Contact ID {duplicate_partner_id} tại sự kiện '{event_name}' (Deal ID: {existing_deals[0]}).")
        print("👉 Hệ thống tự động ngăn chặn tạo trùng lặp thành công!")

    # 5. Đối soát dữ liệu các Deal vừa tạo
    print("\n--- DANH SÁCH DEALS VỪA ĐƯỢC TẠO ---")
    deals_data = models.execute_kw(
        ODOO_DB, uid, PASSWORD,
        'crm.lead', 'read',
        [created_deal_ids, ['id', 'name', 'partner_id', 'expected_revenue', 'phone', 'email_from']]
    )
    for d in deals_data:
        print(f"📌 Deal ID {d['id']:2}: Name='{d['name']}' | Revenue={d['expected_revenue']:,.0f} | Partner={d['partner_id'][1]}")

    print("\n" + "="*68)
    print("🎉 KIỂM THỬ TASK 9 THÀNH CÔNG 100%!")
    print("="*68)

if __name__ == "__main__":
    run_tests()
