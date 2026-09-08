import os
import logging
import traceback
from datetime import datetime, timezone, timedelta
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from common.audit_logger import log_change, get_now_vn_str

load_dotenv()

VN_TZ = timezone(timedelta(hours=7))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task1_Sync")

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "HubSpot_Data_Sync")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

HEADERS_ORDER = [
    "HubSpot Contact ID", "First Name", "Last Name", "Email", "Phone",
    "Mobile Phone", "Company", "Job Title", "Website", "Country",
    "Lifecycle Stage", "Create Date", "Last Modified Date", "last_sync"
]

FIELD_NAMES = HEADERS_ORDER[:-1]

def get_google_sheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

def log_error_to_sheet(sheet, error_msg):
    """Ghi log lỗi vào tab Sync_Errors theo đúng yêu cầu"""
    try:
        ws_err = sheet.worksheet("Sync_Errors")
    except gspread.WorksheetNotFound:
        ws_err = sheet.add_worksheet(title="Sync_Errors", rows=100, cols=5)
        ws_err.append_row(["Timestamp (VN)", "Task", "Error Message", "Status"])
    
    ws_err.append_row([get_now_vn_str(), "Task 1: HubSpot -> Sheet", str(error_msg), "ERROR"])

def fetch_all_hubspot_contacts():
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
    properties = [
        "firstname", "lastname", "email", "phone", "mobilephone",
        "company", "jobtitle", "website", "country", "lifecyclestage",
        "createdate", "lastmodifieddate"
    ]
    params = {"limit": 100, "properties": ",".join(properties)}
    
    contacts = []
    after = None
    while True:
        if after:
            params["after"] = after
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            raise Exception(f"Lỗi gọi HubSpot: {res.status_code} - {res.text}")
        data = res.json()
        contacts.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
    return contacts

def sync_contacts():
    now_vn_str = get_now_vn_str()
    # Yêu cầu: Tên sheet theo format Contacts_YYYY_MM_DD
    today_str = datetime.now(VN_TZ).strftime("%Y_%m_%d")
    dynamic_sheet_name = f"Contacts_{today_str}"
    
    logger.info(f"🔄 Bắt đầu đối soát Contact. Dữ liệu sẽ lưu vào tab: {dynamic_sheet_name}")

    client = get_google_sheet_client()
    sheet = client.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else client.open(SPREADSHEET_NAME)

    try:
        raw_contacts = fetch_all_hubspot_contacts()
    except Exception as e:
        logger.error(f"Failed to fetch contacts: {e}")
        log_error_to_sheet(sheet, str(e))
        return

    try:
        ws = sheet.worksheet(dynamic_sheet_name)
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title=dynamic_sheet_name, rows=100, cols=20)
        ws.append_row(HEADERS_ORDER)

    existing_rows = ws.get_all_values()
    old_data_map = {str(r[0]).strip(): r for r in existing_rows[1:] if r and r[0]}

    current_hubspot_ids = set()
    rows_to_write = [HEADERS_ORDER]
    created_count, updated_count = 0, 0

    for item in raw_contacts:
        cid = str(item.get("id"))
        current_hubspot_ids.add(cid)
        p = item.get("properties", {})
        
        new_row_values = [
            cid, p.get("firstname") or "", p.get("lastname") or "", p.get("email") or "",
            p.get("phone") or "", p.get("mobilephone") or "", p.get("company") or "",
            p.get("jobtitle") or "", p.get("website") or "", p.get("country") or "",
            p.get("lifecyclestage") or "", p.get("createdate") or "", p.get("lastmodifieddate") or ""
        ]

        if cid not in old_data_map:
            created_count += 1
            log_change("CREATE", "Contact", cid, "HubSpot", p.get("email") or "HubSpot User", [{"field": "Info", "old": "", "new": f"{p.get('firstname')} {p.get('lastname')}"}])
        else:
            old_row = old_data_map[cid]
            field_diffs = [{"field": f_name, "old": old_row[i] if i < len(old_row) else "", "new": new_val} 
                           for i, (f_name, new_val) in enumerate(zip(FIELD_NAMES, new_row_values)) 
                           if str(old_row[i] if i < len(old_row) else "").strip() != str(new_val).strip()]
            if field_diffs:
                updated_count += 1
                log_change("UPDATE", "Contact", cid, "HubSpot", p.get("email") or "HubSpot User", field_diffs)

        rows_to_write.append(new_row_values + [now_vn_str])

    deleted_ids = set(old_data_map.keys()) - current_hubspot_ids
    for d_id in deleted_ids:
        log_change("DELETE", "Contact", d_id, "HubSpot", "Admin", [{"field": "Status", "old": "Active", "new": "Deleted"}])

    ws.clear()
    ws.update(values=rows_to_write, range_name="A1")

    logger.info(f"✅ TỔNG KẾT: CRM {len(raw_contacts)} | Mới {created_count} | Sửa {updated_count} | Xóa {len(deleted_ids)}")

if __name__ == "__main__":
    sync_contacts()
