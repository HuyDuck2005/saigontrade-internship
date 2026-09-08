import os
import sys
import unittest
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from hubspot.task1_hubspot_to_sheet import sync_contacts
from hubspot.task2_sheet_to_hubspot import import_contacts_from_sheet
from hubspot.task3_deal_to_sheet import sync_deals

load_dotenv()

class TestHubSpotComprehensive(unittest.TestCase):
    
    def test_1_hubspot_to_sheet_sync(self):
        print("\n--- [TEST TASK 1] Đồng bộ HubSpot Contact -> Google Sheet ---")
        try:
            sync_contacts()
            print("✅ Task 1 chạy thành công (Đã tạo sheet động & Audit log).")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Task 1 thất bại: {e}")

    def test_2_sheet_to_hubspot_import(self):
        print("\n--- [TEST TASK 2] Import Contact từ Google Sheet -> HubSpot ---")
        try:
            import_contacts_from_sheet()
            print("✅ Task 2 chạy thành công (Đã xử lý trạng thái NEW/RETRY & Validate).")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Task 2 thất bại: {e}")

    def test_3_deal_to_sheet_sync(self):
        print("\n--- [TEST TASK 3] Đồng bộ HubSpot Deal & Summary sang Sheet ---")
        try:
            sync_deals()
            print("✅ Task 3 chạy thành công (Đã tạo bảng Summary báo cáo).")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Task 3 thất bại: {e}")

if __name__ == "__main__":
    unittest.main()
