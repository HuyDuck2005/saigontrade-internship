import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from odoo.task8_deal_middleware import app, API_MIDDLEWARE_KEY

client = TestClient(app)

class TestMiddlewareCases(unittest.TestCase):

    def test_case_1_unauthorized_missing_key(self):
        print("\n--- [TEST TASK 8 - CASE 1] Chặn truy cập khi thiếu X-API-Key ---")
        res = client.post("/api/crm/deal", json={"deal_name": "Test Unauth"})
        self.assertEqual(res.status_code, 401)

    def test_case_2_success_create_deal_and_contact(self):
        print("\n--- [TEST TASK 8 - CASE 2] Tạo Deal & Contact qua Middleware thành công ---")
        payload = {
            "deal_name": "Gói Giải Pháp Doanh Nghiệp 2026",
            "firstname": "Trần",
            "lastname": "Hải Nam",
            "phone": "0988112233",
            "email": "namth@sgtcorp.vn",
            "expected_revenue": 1000,
            "currency": "USD" # Test quy đổi ngoại tệ sang VND
        }
        headers = {
            "X-API-Key": API_MIDDLEWARE_KEY,
            "Idempotency-Key": "test-idempotency-unique-999"
        }
        res = client.post("/api/crm/deal", json=payload, headers=headers)
        print(f"Response status: {res.status_code} | Data: {res.json()}")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.json()["success"])
        # Kiểm tra quy đổi USD sang VND (1000 * 25400 = 25400000.0)
        self.assertEqual(res.json()["converted_revenue_vnd"], 25400000.0)

    def test_case_3_idempotency_prevention(self):
        print("\n--- [TEST TASK 8 - CASE 3] Kiểm tra chống tạo trùng bằng Idempotency-Key ---")
        payload = {
            "deal_name": "Deal Trùng Lặp Idempotency",
            "phone": "0911223344"
        }
        headers = {
            "X-API-Key": API_MIDDLEWARE_KEY,
            "Idempotency-Key": "duplicate-key-xyz"
        }
        res1 = client.post("/api/crm/deal", json=payload, headers=headers)
        res2 = client.post("/api/crm/deal", json=payload, headers=headers)
        
        # Cả 2 lần gọi phải trả về cùng một Deal ID do dính cache Idempotency
        self.assertEqual(res1.status_code, 201)
        self.assertEqual(res2.status_code, 201)
        self.assertEqual(res1.json()["deal_id"], res2.json()["deal_id"])

if __name__ == "__main__":
    unittest.main()
