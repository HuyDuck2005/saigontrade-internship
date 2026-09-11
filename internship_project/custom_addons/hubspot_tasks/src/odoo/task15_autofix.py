import os
import sys
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task15_AutoFix")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo_db")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

def auto_fix_discrepancies():
    logger.info("🛠️ Bắt đầu quét và tự động sửa lệch dữ liệu (Auto-Fix)...")
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    doc = client.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else client.open("HubSpot_Data_Sync")

    try:
        ws_recon = doc.worksheet("Reconciliation")
    except Exception:
        logger.error("Chưa có tab Reconciliation để fix!")
        return

    rows = ws_recon.get_all_values()
    if len(rows) <= 1:
        logger.info("Không có dữ liệu lệch cần fix.")
        return

    fixed_count = 0
    for idx, r in enumerate(rows[1:], start=2):
        entity_id_str = r[0] # Ví dụ: Deal #15
        field_name = r[1]
        odoo_val = r[2]
        sheet_val = r[3]
        status = r[4]

        # Fix Case 1: Lệch tên Deal -> Đồng bộ lấy giá trị chuẩn từ Odoo sang Sheet
        if "Deal Name" in field_name and "Lệch" in status:
            clean_id = entity_id_str.replace("Deal #", "").strip()
            # Cập nhật lại tab Deals trên Sheet
            try:
                ws_deals = doc.worksheet("Deals")
                cell = ws_deals.find(clean_id, in_column=1)
                if cell:
                    ws_deals.update_cell(cell.row, 2, odoo_val)
                    ws_recon.update_cell(idx, 5, "ĐÃ TỰ ĐỘNG SỬA (AUTO-FIXED)")
                    fixed_count += 1
            except Exception as e:
                logger.error(f"Lỗi fix dòng {idx}: {e}")

        # Fix Case 2: Chỉ có trên Odoo -> Tự động chèn bổ sung vào Sheet tab Deals
        elif "Chỉ có trên Odoo" in status:
            clean_id = entity_id_str.replace("Deal #", "").strip()
            try:
                ws_deals = doc.worksheet("Deals")
                ws_deals.append_row([clean_id, odoo_val, "0", "default", "New", "", datetime.now().strftime("%Y-%m-%d"), "", "", ""])
                ws_recon.update_cell(idx, 5, "ĐÃ TỰ ĐỘNG SỬA (BỔ SUNG SHEET)")
                fixed_count += 1
            except Exception as e:
                logger.error(f"Lỗi append dòng {idx}: {e}")

    logger.info(f"✅ Auto-fix hoàn tất! Đã xử lý {fixed_count} bản ghi lệch.")

if __name__ == "__main__":
    auto_fix_discrepancies()
