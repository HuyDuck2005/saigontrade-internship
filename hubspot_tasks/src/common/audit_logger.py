import os
import json
import csv
from datetime import datetime, timezone, timedelta
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

VN_TZ = timezone(timedelta(hours=7))
LOG_JSON_FILE = "audit_change_log.json"
LOG_CSV_FILE = "audit_change_log.csv"
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "HubSpot_Data_Sync")

AUDIT_HEADERS = [
    "Thời gian (VN)",
    "Hành động",
    "Đối tượng",
    "Mã ID",
    "Nguồn thay đổi",
    "Người thực hiện",
    "Chi tiết thay đổi (Trường: Cũ -> Mới)"
]

def get_now_vn_str():
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")

def log_change(action: str, entity_type: str, entity_id: str, source: str, actor: str, changes: list):
    """
    changes là danh sách các thay đổi, ví dụ:
    [{"field": "phone", "old": "0911222", "new": "0988999"}, ...]
    """
    timestamp = get_now_vn_str()
    
    # Định dạng chuỗi chi tiết thay đổi
    if not changes:
        details_str = "Tạo mới hoặc đồng bộ nguyên trạng"
    else:
        change_parts = []
        for c in changes:
            field = c.get("field", "")
            old_val = c.get("old", "")
            new_val = c.get("new", "")
            if old_val != new_val:
                change_parts.append(f"[{field}]: '{old_val}' ➔ '{new_val}'")
        details_str = " | ".join(change_parts) if change_parts else "Không có thay đổi dữ liệu"

    record_dict = {
        "timestamp": timestamp,
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "source": source,
        "actor": actor,
        "details": details_str,
        "raw_changes": changes
    }

    # 1. Ghi vào file JSON (Tích lũy lịch sử đầy đủ)
    all_logs = []
    if os.path.exists(LOG_JSON_FILE):
        try:
            with open(LOG_JSON_FILE, "r", encoding="utf-8") as f:
                all_logs = json.load(f)
        except Exception:
            all_logs = []
    all_logs.append(record_dict)
    with open(LOG_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_logs, f, indent=2, ensure_ascii=False)

    # 2. Ghi vào file CSV (Thuận tiện mở bằng Excel)
    file_exists = os.path.exists(LOG_CSV_FILE)
    with open(LOG_CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(AUDIT_HEADERS)
        writer.writerow([
            timestamp, action, entity_type, str(entity_id), source, actor, details_str
        ])

    # 3. Ghi vào tab Audit_Logs trên Google Sheet
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else client.open(SPREADSHEET_NAME)
        
        try:
            ws_audit = sheet.worksheet("Audit_Logs")
        except gspread.WorksheetNotFound:
            ws_audit = sheet.add_worksheet(title="Audit_Logs", rows=100, cols=10)
            ws_audit.append_row(AUDIT_HEADERS)
            
        ws_audit.append_row([
            timestamp, action, entity_type, str(entity_id), source, actor, details_str
        ])
    except Exception as e:
        print(f"⚠️ Không thể đẩy audit log lên Sheet: {e}")

