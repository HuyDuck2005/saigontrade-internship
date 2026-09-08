import os
import sys
import unittest
import xmlrpc.client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from odoo.task5_odoo_create_lead import OdooCRMClient, ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
from odoo.task7_custom_field_mapper import OdooFieldMapper

class TestOdooAdvanced(unittest.TestCase):

    def setUp(self):
        self.client = OdooCRMClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

    def test_case_1_create_lead_success(self):
        print("\n--- [TEST TASK 5 - CASE 1] Tạo CRM Lead thành công ---")
        lead_data = {
            "name": "Dự án Chuyển đổi số SGT 2026",
            "contact_name": "Lương Thế Vinh",
            "phone": "0912345678",
            "email_from": "vinhlt@sgt.vn",
            "expected_revenue": 50000000.0,
            "description": "Test case tạo lead tự động từ script."
        }
        res = self.client.create_lead(lead_data)
        print(f"Kết quả trả về: {res}")
        self.assertTrue(res["success"])
        self.assertIn("lead_id", res)

    def test_case_2_create_lead_missing_name(self):
        print("\n--- [TEST TASK 5 - CASE 2] Bắt lỗi khi thiếu trường 'name' ---")
        with self.assertRaises(ValueError):
            self.client.create_lead({"name": "", "contact_name": "Test Missing Name"})

    def test_case_3_custom_field_mapper(self):
        print("\n--- [TEST TASK 7] Kiểm thử ánh xạ Custom Fields động ---")
        c2 = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
        uid2 = c2.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        m2 = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
        
        mapper = OdooFieldMapper(m2, ODOO_DB, uid2, ODOO_PASSWORD, target_model='res.partner')
        sample_data = {
            'name': 'Nguyễn Văn Test Mapping',
            'phone': '0999888777',
            'x_firstname': 'Văn',
            'x_lastname': 'Nguyễn',
            'x_jobtitle': 'Technical Lead',
            'x_event': 'SGT TechFest 2026'
        }
        mapped_vals, report = mapper.map_and_sanitize(sample_data)
        print(f"Báo cáo mapping trường: {report}")
        self.assertIn('name', mapped_vals)
        self.assertTrue(len(mapped_vals) > 0)

if __name__ == "__main__":
    unittest.main()
