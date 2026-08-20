import os
import sys

# Thêm đường dẫn src vào PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hubspot.task1_hubspot_to_sheet import sync_contacts
from hubspot.task2_sheet_to_hubspot import import_contacts_from_sheet
from hubspot.task3_deal_to_sheet import sync_deals
from odoo.task5_odoo_create_lead import OdooCRMClient, ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

def show_menu():
    while True:
        print("\n" + "#" * 58)
        print("     HỆ THỐNG ĐIỀU KHIỂN TÍCH HỢP HUBSPOT & ODOO CRM")
        print("#" * 58)
        print("  --- HUBSPOT & GOOGLE SHEETS ---")
        print("  [1] Task 1: Đồng bộ Contacts (HubSpot -> Sheet)")
        print("  [2] Task 2: Import Contacts (Sheet -> HubSpot)")
        print("  [3] Task 3: Đồng bộ Deals & Báo cáo Summary")
        print("  --- ODOO CRM INTEGRATION ---")
        print("  [4] Task 5: Tạo CRM Lead trong Odoo qua XML-RPC")
        print("  [5] Task 6: Chạy kiểm thử Sync Contact Odoo1 -> Odoo2")
        print("  [6] Task 7: Chạy kiểm thử Field Mapping Odoo1 -> Odoo2")
        print("  [0] Thoát")
        print("#" * 58)
        
        choice = input("👉 Nhập lựa chọn (0-6): ").strip()
        
        if choice == '1':
            sync_contacts()
        elif choice == '2':
            import_contacts_from_sheet()
        elif choice == '3':
            sync_deals()
        elif choice == '4':
            client = OdooCRMClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
            client.create_lead({"name": "Test Lead Main CLI", "contact_name": "Nguyen Van Test"})
        elif choice == '5':
            os.system("python3 tests/test_task6_flow.py")
        elif choice == '6':
            os.system("python3 tests/test_task7_mapping.py")
        elif choice == '0':
            print("Tạm biệt!")
            break
        else:
            print("⚠️ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    show_menu()
