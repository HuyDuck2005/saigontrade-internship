import os
import sys
import logging

# Thêm đường dẫn thư mục src vào hệ thống
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from odoo.task5_odoo_create_lead import OdooCRMClient, ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("TestTask5Real")

def run_real_tests():
    print("\n" + "="*65)
    print("🚀 BẮT ĐẦU TEST TASK 5 TRỰC TIẾP TRÊN MÁY CHỦ ODOO DOCKER")
    print("="*65)

    client = OdooCRMClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

    # Test Case 1: Tạo Lead thật đầy đủ dữ liệu
    print("\n[TEST CASE 1] Tạo Lead thành công đầy đủ trường trên Odoo:")
    lead_data_1 = {
        "name": "Cơ hội hợp tác - Doanh nghiệp SGT 2026",
        "contact_name": "Trần Văn Nam",
        "phone": "0988776655",
        "email": "nam.tran@example.com",
        "event": "Vietnam TechExpo 2026",
        "event_location": "TP. Hồ Chí Minh",
        "description": "Quan tâm đến giải pháp tích hợp CRM và ERP."
    }
    res1 = client.create_lead(lead_data_1)
    print(f"👉 Kết quả Case 1: {res1}")

    # Test Case 2: Kiểm tra bắt lỗi validation thiếu trường name
    print("\n[TEST CASE 2] Bắt lỗi khi thiếu trường 'name' bắt buộc:")
    try:
        client.create_lead({"name": "", "contact_name": "Test Missing Name"})
    except ValueError as val_err:
        print(f"👉 Bắt lỗi thành công (Validation): {val_err}")

    # Test Case 3: Bắt lỗi khi sai mật khẩu Odoo
    print("\n[TEST CASE 3] Bắt lỗi khi sai tài khoản / mật khẩu Odoo:")
    bad_client = OdooCRMClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, "mat_khau_sai_123")
    res3 = bad_client.create_lead(lead_data_1)
    print(f"👉 Kết quả Case 3: {res3}")

    print("\n" + "="*65)
    print("✅ HOÀN TẤT KIỂM THỬ TASK 5 TRÊN MÁY CHỦ ODOO!")
    print("="*65)

if __name__ == "__main__":
    run_real_tests()
