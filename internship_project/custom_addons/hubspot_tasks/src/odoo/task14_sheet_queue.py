import os
import sys
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from odoo.task5_odoo_create_lead import OdooCRMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task14_Standard_Queue")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
QUEUE_TAB = "Queue"

def get_queue_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    doc = client.open_by_key(SPREADSHEET_ID)
    return doc.worksheet(QUEUE_TAB)

def process_queue():
    if not os.path.exists(CREDENTIALS_FILE):
        logger.error(f" Không tìm thấy file {CREDENTIALS_FILE}")
        return

    sheet = get_queue_sheet()
    logger.info(f" Kết nối Google Sheet thành công: tab [{QUEUE_TAB}]")
    
    rows = sheet.get_all_values()
    if len(rows) <= 1:
        logger.info("Hàng đợi không có dữ liệu cần xử lý.")
        return

    headers = rows[0]
    
    # Ánh xạ chỉ mục các cột
    col_map = {h: idx + 1 for idx, h in enumerate(headers)}
    status_col = col_map.get("Status", 1)
    odoo_id_col = col_map.get("Odoo Deal ID")
    updated_col = col_map.get("Updated At")

    odoo_client = OdooCRMClient(
        os.getenv("ODOO_URL", "http://localhost:8069"),
        os.getenv("ODOO_DB", "odoo_db"),
        os.getenv("ODOO_USERNAME", "admin"),
        os.getenv("ODOO_PASSWORD", "admin")
    )

    for idx, row in enumerate(rows[1:], start=2):
        status = str(row[status_col - 1]).strip().upper()
        if status != "NEW":
            continue

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f" Dòng {idx} -> Cập nhật trạng thái: PROCESSING...")
        sheet.update_cell(idx, status_col, "PROCESSING")
        if updated_col:
            sheet.update_cell(idx, updated_col, now_str)

        # Mapping dữ liệu an toàn
        deal_name = row[col_map["Deal Name"] - 1] if "Deal Name" in col_map else f"Deal #{idx}"
        contact_name = row[col_map["Contact Name"] - 1] if "Contact Name" in col_map else ""
        email = row[col_map["Email"] - 1] if "Email" in col_map else ""
        phone = row[col_map["Phone"] - 1] if "Phone" in col_map else ""

        lead_data = {
            "name": deal_name,
            "contact_name": contact_name,
            "email_from": email,
            "phone": phone
        }

        try:
            res = odoo_client.create_lead(lead_data)
            if res.get("success"):
                lead_id = res["lead_id"]
                logger.info(f" Tạo Odoo Lead ID {lead_id} thành công -> Cập nhật: DONE")
                sheet.update_cell(idx, status_col, "DONE")
                if odoo_id_col:
                    sheet.update_cell(idx, odoo_id_col, str(lead_id))
                if updated_col:
                    sheet.update_cell(idx, updated_col, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                logger.error(f" Lỗi Odoo dòng {idx}: {res.get('error')}")
                sheet.update_cell(idx, status_col, "ERROR")
        except Exception as e:
            logger.error(f" Ngoại lệ dòng {idx}: {e}")
            sheet.update_cell(idx, status_col, "ERROR")

if __name__ == "__main__":
    process_queue()
