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
logger = logging.getLogger("Task15_Reconciliation")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo_db")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

RECON_HEADERS = ["Đối tượng / ID", "Trường đối soát", "Giá trị Odoo", "Giá trị Sheet", "Trạng thái lệch", "Thời gian quét"]

def get_sheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

def reconcile_odoo_and_sheet():
    logger.info("🔍 Bắt đầu chạy đối soát dữ liệu Odoo CRM <-> Google Sheet...")
    
    # 1. Đọc dữ liệu Odoo
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise ConnectionError("Không thể kết nối Odoo")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    odoo_leads = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "crm.lead", "search_read",
        [[["type", "=", "opportunity"]]],
        {"fields": ["id", "name", "phone", "email_from", "expected_revenue"]}
    )
    odoo_map = {str(d["id"]): d for d in odoo_leads}

    # 2. Đọc dữ liệu Google Sheet tab Deals hoặc Queue
    gc = get_sheet_client()
    doc = gc.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else gc.open("HubSpot_Data_Sync")
    
    # Ưu tiên lấy từ tab Deals nếu có, ngược lại lấy Queue
    try:
        ws_deals = doc.worksheet("Deals")
        sheet_rows = ws_deals.get_all_values()
    except Exception:
        ws_deals = doc.worksheet("Queue")
        sheet_rows = ws_deals.get_all_values()

    sheet_map = {}
    if len(sheet_rows) > 1:
        headers = [h.strip() for h in sheet_rows[0]]
        id_idx = -1
        for cand in ["Deal ID", "Odoo Deal ID", "ID"]:
            if cand in headers:
                id_idx = headers.index(cand)
                break
        
        if id_idx != -1:
            for r in sheet_rows[1:]:
                if len(r) > id_idx and r[id_idx].strip():
                    sheet_map[str(r[id_idx]).strip()] = r

    # 3. So sánh dữ liệu tìm độ lệch
    discrepancies = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Kiểm tra các Deal có trên Odoo
    for o_id, o_data in odoo_map.items():
        if o_id not in sheet_map:
            discrepancies.append([f"Deal #{o_id}", "Existence", o_data.get("name"), "Chưa có trên Sheet", "Chỉ có trên Odoo", now_str])
        else:
            s_row = sheet_map[o_id]
            # So sánh tên deal (giả sử cột 1 trên sheet)
            s_name = s_row[1] if len(s_row) > 1 else ""
            if o_data.get("name") and s_name and o_data.get("name").strip() != s_name.strip():
                discrepancies.append([f"Deal #{o_id}", "Deal Name", o_data.get("name"), s_name, "Lệch thông tin", now_str])

    # Kiểm tra các Deal chỉ có trên Sheet
    for s_id, s_row in sheet_map.items():
        if s_id not in odoo_map and s_id.isdigit():
            s_name = s_row[1] if len(s_row) > 1 else ""
            discrepancies.append([f"Deal #{s_id}", "Existence", "Không tìm thấy trong Odoo", s_name, "Chỉ có trên Sheet", now_str])

    # 4. Xuất kết quả vào tab Reconciliation
    try:
        ws_recon = doc.worksheet("Reconciliation")
    except gspread.WorksheetNotFound:
        ws_recon = doc.add_worksheet(title="Reconciliation", rows=100, cols=10)

    ws_recon.clear()
    if not discrepancies:
        ws_recon.append_row(RECON_HEADERS)
        ws_recon.append_row(["Tất cả", "Toàn bộ dữ liệu", "Khớp 100%", "Khớp 100%", "ĐỒNG BỘ HOÀN HẢO", now_str])
        logger.info("✅ Dữ liệu Odoo và Sheet khớp 100%, không phát hiện sai lệch!")
    else:
        ws_recon.append_row(RECON_HEADERS)
        for row in discrepancies:
            ws_recon.append_row(row)
        logger.info(f"⚠️ Đã phát hiện {len(discrepancies)} điểm lệch dữ liệu và lưu vào tab Reconciliation!")

if __name__ == "__main__":
    reconcile_odoo_and_sheet()
