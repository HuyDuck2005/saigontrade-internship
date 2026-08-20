import os
import re
import logging
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from audit_logger import log_change

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task2_Import")

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "HubSpot_Data_Sync")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

HEADERS = [
    "firstname", "lastname", "email", "phone", "mobilephone",
    "jobtitle", "company", "website", "country", "event",
    "event_location", "status", "HubSpot ID", "error_message"
]

def is_valid_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(email).strip()))

def get_google_sheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

def hubspot_search_contact(email=None, phone=None):
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
    filters = []
    if email and is_valid_email(email):
        filters.append({"propertyName": "email", "operator": "EQ", "value": email.strip()})
    elif phone:
        filters.append({"propertyName": "phone", "operator": "EQ", "value": str(phone).strip()})
        
    if not filters:
        return None
    payload = {"filterGroups": [{"filters": filters}], "limit": 1}
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        results = res.json().get("results", [])
        if results:
            return results[0]["id"]
    return None

def create_contact(props):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json={"properties": props})
    return res.status_code, res.json()

def update_contact(cid, props):
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{cid}"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
    res = requests.patch(url, headers=headers, json={"properties": props})
    return res.status_code, res.json()

def import_contacts_from_sheet():
    client = get_google_sheet_client()
    sheet = client.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else client.open(SPREADSHEET_NAME)
    
    try:
        ws = sheet.worksheet("Sheet_To_HubSpot")
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Sheet_To_HubSpot", rows=100, cols=20)
        ws.append_row(HEADERS)
        logger.info("Đã tạo tab 'Sheet_To_HubSpot'.")

    all_values = ws.get_all_values()
    if not all_values:
        ws.append_row(HEADERS)
        logger.info("Tab rỗng, đã khởi tạo tiêu đề chuẩn.")
        return

    # Chuẩn hóa tiêu đề dòng 1 nếu bị sai lệch
    if all_values[0] != HEADERS:
        ws.update(values=[HEADERS], range_name="A1:N1")
        all_values[0] = HEADERS

    col_status = HEADERS.index("status") + 1         # Cột 12 (L)
    col_id = HEADERS.index("HubSpot ID") + 1         # Cột 13 (M)
    col_err = HEADERS.index("error_message") + 1     # Cột 14 (N)

    success_cnt, updated_cnt, error_cnt = 0, 0, 0

    # Duyệt từ dòng 2
    for r_idx, row in enumerate(all_values[1:], start=2):
        # Mở rộng dòng nếu bị thiếu cột
        while len(row) < len(HEADERS):
            row.append("")

        status_val = str(row[col_status - 1]).strip().upper()
        
        # Bỏ qua nếu status không phải NEW hoặc RETRY
        if status_val not in ["NEW", "RETRY"]:
            continue

        email = str(row[2]).strip()
        phone = str(row[3]).strip()
        firstname = str(row[0]).strip()
        lastname = str(row[1]).strip()

        logger.info(f"👉 Đang xử lý Dòng {r_idx}: Name='{firstname} {lastname}' | Email='{email}' | Phone='{phone}'")

        if not email and not phone:
            ws.update_cell(r_idx, col_status, "ERROR")
            ws.update_cell(r_idx, col_err, "Thiếu cả Email và Phone")
            log_change("ERROR", "Contact", f"Row_{r_idx}", "Sheet_To_HubSpot", "Sales User", [{"field": "Validation", "old": "", "new": "Thiếu cả Email và Phone"}])
            error_cnt += 1
            continue

        if email and not is_valid_email(email):
            ws.update_cell(r_idx, col_status, "ERROR")
            ws.update_cell(r_idx, col_err, "Định dạng email không hợp lệ")
            log_change("ERROR", "Contact", f"Row_{r_idx}", "Sheet_To_HubSpot", "Sales User", [{"field": "Email", "old": email, "new": "Sai định dạng email"}])
            error_cnt += 1
            continue

        props = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "phone": phone,
            "mobilephone": str(row[4]).strip(),
            "jobtitle": str(row[5]).strip(),
            "company": str(row[6]).strip(),
            "website": str(row[7]).strip(),
            "country": str(row[8]).strip()
        }
        props = {k: v for k, v in props.items() if v}

        try:
            existing_cid = hubspot_search_contact(email=email, phone=phone)
            if existing_cid:
                code, res = update_contact(existing_cid, props)
                if code == 200:
                    ws.update_cell(r_idx, col_status, "UPDATED")
                    ws.update_cell(r_idx, col_id, existing_cid)
                    ws.update_cell(r_idx, col_err, "")
                    updated_cnt += 1
                    log_change("UPDATE", "Contact", existing_cid, "Sheet_To_HubSpot", "Sales User", [{"field": k, "old": "(Sheet)", "new": v} for k, v in props.items()])
                else:
                    ws.update_cell(r_idx, col_status, "ERROR")
                    ws.update_cell(r_idx, col_err, str(res.get("message", code)))
                    error_cnt += 1
            else:
                code, res = create_contact(props)
                if code == 201:
                    new_cid = res.get("id")
                    ws.update_cell(r_idx, col_status, "SUCCESS")
                    ws.update_cell(r_idx, col_id, new_cid)
                    ws.update_cell(r_idx, col_err, "")
                    success_cnt += 1
                    log_change("CREATE", "Contact", new_cid, "Sheet_To_HubSpot", "Sales User", [{"field": "New Contact", "old": "None", "new": f"{firstname} {lastname} ({email})"}])
                else:
                    ws.update_cell(r_idx, col_status, "ERROR")
                    ws.update_cell(r_idx, col_err, str(res.get("message", code)))
                    error_cnt += 1
        except Exception as e:
            ws.update_cell(r_idx, col_status, "ERROR")
            ws.update_cell(r_idx, col_err, str(e))
            error_cnt += 1

    logger.info(f"--- TỔNG KẾT TASK 2 --- Tạo mới (SUCCESS): {success_cnt} | Cập nhật (UPDATED): {updated_cnt} | Lỗi (ERROR): {error_cnt}")

if __name__ == "__main__":
    import_contacts_from_sheet()
