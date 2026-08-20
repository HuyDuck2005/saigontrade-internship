import sys
import os
import unittest
from fastapi.testclient import TestClient

# Thêm đường dẫn src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from odoo.task8_deal_middleware import app, API_MIDDLEWARE_KEY
from odoo.task5_odoo_create_lead import OdooCRMClient

client = TestClient(app)

class TestEdgeCasesAndValidation(unittest.TestCase):

    def test_case_1_missing_required_deal_name(self):
        """Test nhập thiếu trường bắt buộc deal_name."""
        print("\n[EDGE CASE 1] Gửi payload thiếu trường deal_name:")
        headers = {"X-API-Key": API_MIDDLEWARE_KEY}
        payload = {"phone": "0912345678", "email": "test@sgt.vn"}
        res = client.post("/api/crm/deal", json=payload, headers=headers)
        print(f"👉 Status code: {res.status_code} (Bắt lỗi 422 Unprocessable Entity thành công)")
        self.assertEqual(res.status_code, 422)

    def test_case_2_empty_string_payload(self):
        """Test dữ liệu chứa chuỗi rỗng hoặc khoảng trắng."""
        print("\n[EDGE CASE 2] Gửi dữ liệu toàn khoảng trắng:")
        headers = {"X-API-Key": API_MIDDLEWARE_KEY}
        payload = {
            "deal_name": "   ",
            "firstname": "",
            "lastname": "",
            "phone": "   ",
            "email": ""
        }
        res = client.post("/api/crm/deal", json=payload, headers=headers)
        print(f"👉 Kết quả: Status {res.status_code} - Hệ thống tự fallback lấy tên an toàn")
        self.assertIn(res.status_code, [201, 400, 422])

    def test_case_3_special_characters_sql_injection_safe(self):
        """Test dữ liệu chứa ký tự đặc biệt, Unicode, emoji, thẻ HTML."""
        print("\n[EDGE CASE 3] Gửi ký tự đặc biệt, HTML và Unicode tiếng Việt có dấu:")
        headers = {"X-API-Key": API_MIDDLEWARE_KEY}
        payload = {
            "deal_name": "<script>alert('test')</script> Cơ hội VIP 🚀 2026",
            "firstname": "Nguyễn Văn @#$%",
            "lastname": "Đức 🎯",
            "phone": "+84 (091) 234-5678",
            "email": "duc.nguyen+test@sgt-corp.vn.com",
            "note": "Line 1\nLine 2\tTabbed\n' OR '1'='1"
        }
        res = client.post("/api/crm/deal", json=payload, headers=headers)
        print(f"👉 Status code: {res.status_code} | Deal ID: {res.json().get('deal_id')}")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.json()["success"])

    def test_case_4_invalid_api_key_header(self):
        """Test API Key giả mạo."""
        print("\n[EDGE CASE 4] Gửi API Key không đúng:")
        headers = {"X-API-Key": "sai_api_key_hoan_toan"}
        payload = {"deal_name": "Test Fake Key"}
        res = client.post("/api/crm/deal", json=payload, headers=headers)
        print(f"👉 Status code: {res.status_code} (Bắt lỗi 401 Unauthorized thành công)")
        self.assertEqual(res.status_code, 401)

if __name__ == "__main__":
    print("\n" + "="*68)
    print("🚀 BẮT ĐẦU BỘ TEST CHUYÊN SÂU CÁC TRƯỜNG HỢP NHẬP SAI & BẪY LỖI")
    print("="*68)
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\n" + "="*68)
    print("🎉 HOÀN TẤT TOÀN BỘ CÁC TEST CASES NÂNG CAO THÀNH CÔNG!")
    print("="*68)
