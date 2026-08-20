import os
import logging
from datetime import datetime, timezone, timedelta
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from audit_logger import log_change, get_now_vn_str

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

FIELD_NAMES = [
    "HubSpot Contact ID", "First Name", "Last Name", "Email", "Phone",
    "Mobile Phone", "Company", "Job Title", "Website", "Country",
    "Lifecycle Stage", "Create Date", "Last Modified Date"
]

def get_google_sheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

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
            logger.error(f"Lỗi gọi HubSpot: {res.status_code} - {res.text}")
            break
        data = res.json()
        contacts.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
            
    return contacts

def sync_contacts():
    now_vn_str = get_now_vn_str()
    logger.info("🔄 Bắt đầu kiểm tra và đối soát Contact từ HubSpot...")

    raw_contacts = fetch_all_hubspot_contacts()
    total_hubspot = len(raw_contacts)

    client = get_google_sheet_client()
    sheet = client.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else client.open(SPREADSHEET_NAME)

    try:
        ws = sheet.worksheet("Contacts")
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Contacts", rows=100, cols=20)
        ws.append_row(HEADERS_ORDER)

    existing_rows = ws.get_all_values()
    old_data_map = {}
    if len(existing_rows) > 1:
        for r in existing_rows[1:]:
            if r and r[0]:
                cid = str(r[0]).strip()
                # Lưu trữ toàn bộ các cột cũ để so sánh
                old_data_map[cid] = r

    current_hubspot_ids = set()
    rows_to_write = [HEADERS_ORDER]
    
    created_count = 0
    updated_count = 0

    for item in raw_contacts:
        cid = str(item.get("id"))
        current_hubspot_ids.add(cid)
        p = item.get("properties", {})
        
        new_row_values = [
            cid,
            p.get("firstname") or "",
            p.get("lastname") or "",
            p.get("email") or "",
            p.get("phone") or "",
            p.get("mobilephone") or "",
            p.get("company") or "",
            p.get("jobtitle") or "",
            p.get("website") or "",
            p.get("country") or "",
            p.get("lifecyclestage") or "",
            p.get("createdate") or "",
            p.get("lastmodifieddate") or ""
        ]

        if cid not in old_data_map:
            # CREATE mới
            created_count += 1
            log_change(
                action="CREATE",
                entity_type="Contact",
                entity_id=cid,
                source="HubSpot CRM",
                actor=p.get("email") or "HubSpot User",
                changes=[{"field": "Full Info", "old": "None", "new": f"{p.get('firstname', '')} {p.get('lastname', '')} ({p.get('email', '')})"}]
            )
        else:
            # So sánh từng trường để tìm khác biệt
            old_row = old_data_map[cid]
            field_diffs = []
            for i, f_name in enumerate(FIELD_NAMES):
                old_val = old_row[i] if i < len(old_row) else ""
                new_val = new_row_values[i]
                if str(old_val).strip() != str(new_val).strip():
                    field_diffs.append({"field": f_name, "old": old_val, "new": new_val})
            
            if field_diffs:
                updated_count += 1
                log_change(
                    action="UPDATE",
                    entity_type="Contact",
                    entity_id=cid,
                    source="HubSpot CRM",
                    actor=p.get("email") or "HubSpot User",
                    changes=field_diffs
                )

        rows_to_write.append(new_row_values + [now_vn_str])

    # Kiểm tra liên hệ bị xóa khỏi HubSpot
    old_ids = set(old_data_map.keys())
    deleted_ids = old_ids - current_hubspot_ids
    for d_id in deleted_ids:
        log_change(
            action="DELETE",
            entity_type="Contact",
            entity_id=d_id,
            source="HubSpot CRM",
            actor="HubSpot Admin",
            changes=[{"field": "Status", "old": "Active", "new": "Deleted/Trash"}]
        )

    # Ghi đè cập nhật Sheet
    ws.clear()
    ws.update(values=rows_to_write, range_name="A1")

    logger.info("==================== TỔNG KẾT ĐỐI SOÁT TASK 1 ====================")
    logger.info(f"Tổng CRM: {total_hubspot} | Thêm mới: {created_count} | Thay đổi: {updated_count} | Đã xóa: {len(deleted_ids)}")
    logger.info(f"Đã ghi log chi tiết vào 'audit_change_log.csv', 'audit_change_log.json' và tab 'Audit_Logs'")
    logger.info("=================================================================")

if __name__ == "__main__":
    sync_contacts()
