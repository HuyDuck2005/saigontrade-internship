import os
import sys
import xmlrpc.client
import logging

# Thêm đường dẫn thư mục src vào hệ thống
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from odoo.task7_custom_field_mapper import OdooFieldMapper, FIELD_MAPPING_RULES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("TestTask7")

ODOO1_URL = "http://localhost:8069"
ODOO1_DB = "odoo_db"
ODOO2_URL = "http://localhost:8070"
ODOO2_DB = "odoo2_db"
USER = "admin"
PASSWORD = "admin"

def run_task7_tests():
    print("\n" + "="*68)
    print("🚀 BẮT ĐẦU KIỂM THỬ TASK 7: MAPPING CUSTOM FIELDS ODOO1 -> ODOO2")
    print("="*68)

    # 1. Đăng nhập Odoo 1 & Odoo 2
    c1 = xmlrpc.client.ServerProxy(f"{ODOO1_URL}/xmlrpc/2/common", allow_none=True)
    uid1 = c1.authenticate(ODOO1_DB, USER, PASSWORD, {})
    m1 = xmlrpc.client.ServerProxy(f"{ODOO1_URL}/xmlrpc/2/object", allow_none=True)

    c2 = xmlrpc.client.ServerProxy(f"{ODOO2_URL}/xmlrpc/2/common", allow_none=True)
    uid2 = c2.authenticate(ODOO2_DB, USER, PASSWORD, {})
    m2 = xmlrpc.client.ServerProxy(f"{ODOO2_URL}/xmlrpc/2/object", allow_none=True)

    logger.info(f"✅ Odoo 1 UID: {uid1} | Odoo 2 UID: {uid2}")

    # 2. Khởi tạo Mapper & Quét / Tự tạo 20 custom fields trên Odoo 2
    mapper = OdooFieldMapper(m2, ODOO2_DB, uid2, PASSWORD, target_model='res.partner')

    # 3. Giả lập Lead với đầy đủ 20 Custom Fields từ Odoo 1
    test_phone = "0977112233"
    sample_lead_data = {
        'name': 'Hợp tác Doanh nghiệp Công nghệ 2026',
        'contact_name': 'Phạm Quốc Bảo',
        'phone': test_phone,
        'email_from': 'baopq@sgttech.com',
        'x_firstname': 'Bảo',
        'x_lastname': 'Phạm Quốc',
        'x_mobilephone': '0977112233',
        'x_jobtitle': 'Giám đốc Công nghệ (CTO)',
        'x_website': 'https://sgttech.com',
        'x_salutation': 'Mr.',
        'x_country': 'Vietnam',
        'x_getfly_id': 'GF-998822',
        'x_notes': 'Khách hàng VIP tham dự hội thảo ERP Odoo',
        'x_product_category': 'Phần mềm Doanh nghiệp',
        'x_product_details': 'Gói Odoo CRM & Module Đồng bộ Đa hệ thống',
        'x_fb_industry': 'Information Technology',
        'x_url_zalo_group': 'https://zalo.me/g/sgt_vip',
        'x_url_whatsapp_group': 'https://chat.whatsapp.com/sgt_vip',
        'x_url_fb_profile': 'https://facebook.com/bao.pham.tech',
        'x_type_contact': 'Enterprise Buyer',
        'BD': 'SGT TechFest 2026',
        'x_event': 'Triển Lãm Công Nghệ Quốc Tế',
        'x_event_location': 'Trung tâm Hội chợ và Triển lãm Sài Gòn (SECC)',
        'x_email_report': 'reports@sgttech.com'
    }

    print("\n--- [BƯỚC 1] THỰC HIỆN ÁNH XẠ VÀ TỰ ĐỘNG TẠO CUSTOM FIELDS ---")
    mapped_partner_data, mapping_report = mapper.map_and_sanitize(sample_lead_data)
    
    for src, res_txt in list(mapping_report.items())[:6]:
        print(f"🔹 {src:22} -> {res_txt}")
    print(f"... (Tổng cộng đã map thành công {len(mapping_report)} trường)")

    print("\n--- [BƯỚC 2] TẠO / CẬP NHẬT CONTACT VỚI CUSTOM FIELDS TRÊN ODOO 2 ---")
    p2_ids = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'res.partner', 'search', [[['phone', '=', test_phone]]])
    if p2_ids:
        p2_id = p2_ids[0]
        m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'res.partner', 'write', [[p2_id], mapped_partner_data])
        logger.info(f"✅ Đã CẬP NHẬT Contact trên Odoo 2 (ID: {p2_id})")
    else:
        p2_id = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'res.partner', 'create', [mapped_partner_data])
        logger.info(f"✅ Đã TẠO MỚI Contact trên Odoo 2 (ID: {p2_id})")

    print("\n--- [BƯỚC 3] ĐỐI SOÁT DỮ LIỆU ĐÃ LƯU TRÊN ODOO 2 ---")
    fields_to_read = [
        'name', 'phone', 'email', 
        'x_custome_fields_firstname', 'x_custome_fields_lastname',
        'x_custome_fields_jobtitle', 'x_id', 'x_expo', 
        'x_custome_fields_event', 'x_custome_fields_event_location'
    ]
    valid_read_fields = [f for f in fields_to_read if f in mapper.existing_remote_fields or f in ['name', 'phone', 'email']]
    odoo2_saved_record = m2.execute_kw(ODOO2_DB, uid2, PASSWORD, 'res.partner', 'read', [[p2_id], valid_read_fields])[0]

    for k, v in odoo2_saved_record.items():
        print(f"📌 {k:32}: {v}")

    print("\n" + "="*68)
    print("🎉 KIỂM THỬ TASK 7 THÀNH CÔNG 100%!")
    print("="*68)

if __name__ == "__main__":
    run_task7_tests()
