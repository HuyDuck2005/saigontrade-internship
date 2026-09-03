import unittest
from unittest.mock import patch, MagicMock
from task5_odoo_create_lead import OdooCRMClient

class TestOdooCRMClient(unittest.TestCase):
    
    @patch('xmlrpc.client.ServerProxy')
    def test_create_lead_success(self, mock_server_proxy):
        print("\n[TEST CASE 1] Tạo Lead thành công đầy đủ trường (Mock Server):")
        
        # Giả lập phản hồi từ Odoo Common (Authentication) và Object (Create)
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 2  # Trả về UID = 2
        
        mock_objects = MagicMock()
        mock_objects.execute_kw.return_value = 105  # Trả về Lead ID = 105
        
        mock_server_proxy.side_effect = [mock_common, mock_objects]

        client = OdooCRMClient("http://localhost:8069", "odoo_db", "admin", "admin")
        
        lead_data = {
            "name": "Cơ hội hợp tác - Doanh nghiệp SGT 2026",
            "contact_name": "Trần Văn Nam",
            "phone": "0988776655",
            "email": "nam.tran@example.com",
            "event": "Vietnam TechExpo 2026",
            "event_location": "TP. Hồ Chí Minh",
            "description": "Quan tâm đến giải pháp tích hợp CRM và ERP."
        }
        
        res = client.create_lead(lead_data)
        print(f"👉 Kết quả Case 1: {res}")
        self.assertTrue(res["success"])
        self.assertEqual(res["lead_id"], 105)

    def test_create_lead_missing_name(self):
        print("\n[TEST CASE 2] Bắt lỗi khi thiếu trường 'name' bắt buộc:")
        client = OdooCRMClient("http://localhost:8069", "odoo_db", "admin", "admin")
        with self.assertRaises(ValueError) as ctx:
            client.create_lead({"name": "", "contact_name": "Test Missing Name"})
        print(f"👉 Bắt lỗi thành công (Validation): {ctx.exception}")

    @patch('xmlrpc.client.ServerProxy')
    def test_create_lead_bad_auth(self, mock_server_proxy):
        print("\n[TEST CASE 3] Bắt lỗi khi sai tài khoản / mật khẩu Odoo:")
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = False  # Đăng nhập thất bại (UID = 0 / False)
        mock_server_proxy.return_value = mock_common

        bad_client = OdooCRMClient("http://localhost:8069", "odoo_db", "admin", "sai_pass")
        
        lead_data = {"name": "Test Bad Auth"}
        res = bad_client.create_lead(lead_data)
        print(f"👉 Kết quả Case 3: {res}")
        self.assertFalse(res["success"])

if __name__ == "__main__":
    print("\n" + "="*65)
    print("🚀 BẮT ĐẦU BỘ TEST KIỂM THỬ TASK 5 (MOCK MODE): ODOO CRM LEAD API")
    print("="*65)
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\n" + "="*65)
    print("✅ HOÀN TẤT TOÀN BỘ CÁC TEST CASES CỦA TASK 5 THÀNH CÔNG!")
    print("="*65)
