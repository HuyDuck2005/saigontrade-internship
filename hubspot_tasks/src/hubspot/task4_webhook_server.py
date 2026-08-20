import os
import sys
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv

# Thêm đường dẫn src vào PYTHONPATH để import đúng audit_logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.audit_logger import log_change, get_now_vn_str

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task4_WebhookServer")

app = FastAPI(title="HubSpot Webhook Listener API", version="1.0")

# Bộ nhớ đệm chống xử lý webhook trùng (Idempotency)
PROCESSED_EVENTS = set()

@app.get("/health")
def health_check():
    """Endpoint kiểm tra trạng thái hoạt động."""
    return {"status": "ok", "timestamp": get_now_vn_str()}

@app.post("/hubspot/webhook")
async def receive_hubspot_webhook(events: List[Dict[str, Any]], background_tasks: BackgroundTasks):
    """Nhận và xử lý webhook từ HubSpot sang Google Sheet."""
    if not events:
        raise HTTPException(status_code=400, detail="Empty event payload")

    logger.info(f"📥 Nhận được {len(events)} sự kiện Webhook từ HubSpot.")
    
    for ev in events:
        event_id = str(ev.get("eventId") or ev.get("objectId"))
        
        # Chống xử lý trùng lặp
        if event_id in PROCESSED_EVENTS:
            logger.info(f"⚡ Bỏ qua sự kiện trùng: {event_id}")
            continue
        
        PROCESSED_EVENTS.add(event_id)
        
        # Log vào audit log hệ thống
        log_change(
            action="WEBHOOK_RECEIVED",
            entity_type="HubSpot_Contact",
            entity_id=event_id,
            details=f"Subscription: {ev.get('subscriptionType')} - Prop: {ev.get('propertyName')}"
        )

    return {"status": "accepted", "processed_count": len(events)}
