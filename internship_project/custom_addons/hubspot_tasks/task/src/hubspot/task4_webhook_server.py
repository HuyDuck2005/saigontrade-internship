import os
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Request
from audit_logger import log_change

load_dotenv()

VN_TZ = timezone(timedelta(hours=7))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task4_Webhook_Server")

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

app = FastAPI(title="HubSpot Webhook Server", version="2.0")
processed_event_ids = set()

def get_google_sheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

def fetch_single_contact(contact_id: str):
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
    properties = [
        "firstname", "lastname", "email", "phone", "mobilephone",
        "company", "jobtitle", "website", "country", "lifecyclestage",
        "createdate", "lastmodifieddate"
    ]
    params = {"properties": ",".join(properties)}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json()
    return None

def process_webhook_events(events: List[Dict[str, Any]]):
    now_vn_str = datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")
    client = get_google_sheet_client()
    sheet = client.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else client.open(SPREADSHEET_NAME)
    
    try:
        ws = sheet.worksheet("Contacts")
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Contacts", rows=100, cols=20)
        ws.append_row(HEADERS_ORDER)

    for ev in events:
        event_id = str(ev.get("eventId"))
        if event_id in processed_event_ids:
            continue
        processed_event_ids.add(event_id)

        subscription_type = ev.get("subscriptionType")
        contact_id = str(ev.get("objectId"))

        logger.info(f"📩 Nhận Webhook: EventID={event_id} | Type={subscription_type} | ObjectId={contact_id}")

        contact_data = fetch_single_contact(contact_id)
        if not contact_data:
            continue

        p = contact_data.get("properties", {})
        new_row = [
            contact_id,
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

        existing_rows = ws.get_all_values()
        id_to_row = {str(row[0]).strip(): (idx, row) for idx, row in enumerate(existing_rows[1:], start=2) if row and row[0]}

        if contact_id in id_to_row:
            r_idx, old_row = id_to_row[contact_id]
            diffs = []
            for i, f_name in enumerate(FIELD_NAMES):
                old_val = old_row[i] if i < len(old_row) else ""
                new_val = new_row[i]
                if str(old_val).strip() != str(new_val).strip():
                    diffs.append({"field": f_name, "old": old_val, "new": new_val})

            ws.update(values=[new_row + [now_vn_str]], range_name=f"A{r_idx}:N{r_idx}")
            logger.info(f"🔄 [Webhook Sync] Đã CẬP NHẬT Contact ID {contact_id} vào Sheet hàng {r_idx}")
            log_change("UPDATE", "Contact", contact_id, "Webhook Real-time", p.get("email") or "HubSpot User", diffs)
        else:
            ws.append_row(new_row + [now_vn_str])
            logger.info(f"➕ [Webhook Sync] Đã THÊM MỚI Contact ID {contact_id} vào Sheet")
            log_change("CREATE", "Contact", contact_id, "Webhook Real-time", p.get("email") or "HubSpot User", [{"field": "New Contact", "old": "None", "new": f"{p.get('firstname')} {p.get('lastname')}"}])

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp_vn": datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")}

@app.post("/hubspot/webhook")
async def hubspot_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        events = await request.json()
        if isinstance(events, list):
            background_tasks.add_task(process_webhook_events, events)
        elif isinstance(events, dict):
            background_tasks.add_task(process_webhook_events, [events])
        return {"status": "received", "count": len(events) if isinstance(events, list) else 1}
    except Exception as e:
        logger.error(f"Lỗi Webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("task4_webhook_server:app", host="0.0.0.0", port=8000, reload=True)
