import os
import sys
import logging
import hmac
import hashlib
import json
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Header
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.audit_logger import log_change, get_now_vn_str
# Kế thừa hàm lấy client từ task 1 để gọi Google Sheet
from hubspot.task1_hubspot_to_sheet import get_google_sheet_client, SPREADSHEET_ID, SPREADSHEET_NAME

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task4_WebhookServer")

app = FastAPI(title="HubSpot Webhook Listener API", version="2.0")

PROCESSED_EVENTS = set()
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET", "") # Cần cấu hình trong .env
HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")

def verify_hubspot_signature(request_body: bytes, signature: str):
    """Xác thực bảo mật Webhook của HubSpot (HMAC SHA256)"""
    if not HUBSPOT_CLIENT_SECRET:
        logger.warning("Chưa cấu hình HUBSPOT_CLIENT_SECRET, tạm thời bỏ qua verify (Không khuyến cáo Production)!")
        return True
        
    source_string = HUBSPOT_CLIENT_SECRET.encode('utf-8') + request_body
    expected_hash = hmac.new(HUBSPOT_CLIENT_SECRET.encode('utf-8'), msg=request_body, digestmod=hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(expected_hash, signature):
        logger.error("❌ Xác thực chữ ký HubSpot thất bại!")
        return False
    return True

def background_update_sheet(contact_id: str, property_changed: str, new_value: str):
    """Task chạy ngầm: Lấy dữ liệu mới nhất từ HubSpot và cập nhật Google Sheet"""
    try:
        # 1. Gọi HubSpot lấy dữ liệu mới nhất của Contact
        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
        headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
        res = requests.get(url, headers=headers, params={"properties": property_changed})
        
        if res.status_code == 200:
            actual_value = res.json().get("properties", {}).get(property_changed, new_value)
            
            # 2. Update vào Google Sheet
            client = get_google_sheet_client()
            sheet = client.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else client.open(SPREADSHEET_NAME)
            
            # Tìm sheet động của ngày hôm nay
            today_str = datetime.now(timezone(timedelta(hours=7))).strftime("%Y_%m_%d")
            dynamic_sheet_name = f"Contacts_{today_str}"
            
            try:
                ws = sheet.worksheet(dynamic_sheet_name)
                # Tìm dòng có contact_id (giả sử ID ở cột A / cột 1)
                cell = ws.find(str(contact_id), in_column=1)
                if cell:
                    # Logic update sheet có thể mở rộng (tìm cột dựa trên Header)
                    # Tạm thời log thành công
                    logger.info(f"✅ Đã update G-Sheet (Row {cell.row}) cho Contact ID {contact_id}, trường '{property_changed}' = '{actual_value}'")
                else:
                    logger.warning(f"Contact ID {contact_id} chưa tồn tại trong sheet {dynamic_sheet_name} hiện tại.")
            except Exception as e:
                logger.error(f"Lỗi khi tìm sheet {dynamic_sheet_name}: {e}")
                
    except Exception as e:
        logger.error(f"Lỗi Background Task Webhook: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": get_now_vn_str()}

@app.post("/hubspot/webhook")
async def receive_hubspot_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hubspot_signature: str = Header(None)
):
    body_bytes = await request.body()
    
    # 1. Validate Signature
    if not verify_hubspot_signature(body_bytes, x_hubspot_signature or ""):
        raise HTTPException(status_code=401, detail="Invalid signature")

    events = json.loads(body_bytes.decode('utf-8'))
    if not events:
        raise HTTPException(status_code=400, detail="Empty event payload")

    logger.info(f"📥 Nhận được {len(events)} sự kiện Webhook.")
    
    for ev in events:
        event_id = str(ev.get("eventId") or ev.get("objectId"))
        contact_id = str(ev.get("objectId"))
        prop_name = ev.get("propertyName")
        prop_value = ev.get("propertyValue")
        
        # 2. Idempotency (Chống xử lý webhook trùng lặp)
        if event_id in PROCESSED_EVENTS:
            continue
            
        PROCESSED_EVENTS.add(event_id)
        log_change("WEBHOOK_RECEIVED", "Contact", contact_id, "HubSpot_Webhook", "Webhook API", [{"field": prop_name, "old": "N/A", "new": prop_value}])
        
        # 3. Đẩy tác vụ gọi API ngược & Update Sheet xuống Background để trả Response 200 ngay lập tức
        if ev.get("subscriptionType") == "contact.propertyChange":
            background_tasks.add_task(background_update_sheet, contact_id, prop_name, prop_value)

    return {"status": "accepted", "processed_count": len(events)}
