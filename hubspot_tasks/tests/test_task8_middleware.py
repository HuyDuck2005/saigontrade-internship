import sys
import os
import unittest
from fastapi.testclient import TestClient

# Thêm đường dẫn src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from odoo.task8_deal_middleware import app, API_MIDDLEWARE_KEY

client = TestClient(app)

def run_tests():
    print("\n" + "="*68)
    print("🚀 BẮT ĐẦU KIỂM THỬ TASK 8: API MIDDLEWARE NHẬN LEAD & TẠO CRM DEAL")
    print("="*68)

    # Test Case 1: Lỗi 401 khi không truyền hoặc sai API Key
    print("\n[TEST CASE 1] Bắt lỗi 401 khi thiếu hoặc sai X-API-Key:")
    res1 = client.post("/api/crm/deal", json={"deal_name": "Test Fail Auth"})
    print(f"👉 Status code: {res1.status_code} | Chi tiết: {res1.json()}")
    assert res1.status_code == 401

    # Test Case 2: Tạo Deal và Contact thành công
    print("\n[TEST CASE 2] Tạo Contact và Deal thành công với API Key hợp lệ:")
    payload = {
        "deal_name": "Gói Chuyển Đổi Số Doanh Nghiệp 2026",
        "firstname": "Hoàng",
        "lastname": "Minh Trí",
        "phone": "0966554433",
        "email": "triminh@sgtcorp.vn",
        "source": "Landing Page Web 2026",
        "event": "SGT Digital Expo",
        "note": "Khách hàng cần tư vấn tích hợp CRM và ERP trong tháng 9."
    }
    headers = {
        "X-API-Key": API_MIDDLEWARE_KEY,
        "Idempotency-Key": "req-idempotency-key-001"
    }
    res2 = client.post("/api/crm/deal", json=payload, headers=headers)
    print(f"👉 Status code: {res2.status_code}")
    print(f"👉 Kết quả tạo Deal: {res2.json()}")
    assert res2.status_code == 201
    assert res2.json()["success"] is True
    assert "deal_id" in res2.json()

    # Test Case 3: Kiểm tra cơ chế chống duplicate (Idempotency Key)
    print("\n[TEST CASE 3] Gửi lại cùng Idempotency-Key (Chống tạo trùng):")
    res3 = client.post("/api/crm/deal", json=payload, headers=headers)
    print(f"👉 Status code: {res3.status_code}")
    print(f"👉 Kết quả trả về (Trùng deal_id): {res3.json()}")
    assert res3.status_code == 201
    assert res3.json()["deal_id"] == res2.json()["deal_id"]

    print("\n" + "="*68)
    print("🎉 KIỂM THỬ TASK 8 THÀNH CÔNG 100%!")
    print("="*68)

if __name__ == "__main__":
    run_tests()
