import os
import sys
import xmlrpc.client
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, status, Depends
from pydantic import BaseModel, Field

# Thêm đường dẫn src để gọi common audit logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.audit_logger import log_change, get_now_vn_str

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task8_Middleware")

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo_db")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")
API_MIDDLEWARE_KEY = os.getenv("API_MIDDLEWARE_KEY", "sgt_secret_api_key_2026")

# Bộ nhớ đệm Idempotency chống trùng request
IDEMPOTENCY_CACHE: Dict[str, Any] = {}

class DealPayload(BaseModel):
    deal_name: str = Field(..., description="Tên cơ hội / Deal")
    firstname: Optional[str] = ""
    lastname: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    source: Optional[str] = "Website/App"
    event: Optional[str] = ""
    note: Optional[str] = ""

app = FastAPI(title="SGT Odoo Deal Middleware API", version="1.0")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Xác thực API Key."""
    if not x_api_key or x_api_key != API_MIDDLEWARE_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header"
        )
    return x_api_key

def get_odoo_connection():
    """Kết nối và xác thực với Odoo Server."""
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL.rstrip('/')}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise HTTPException(status_code=500, detail="Không thể kết nối / xác thực Odoo CRM")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL.rstrip('/')}/xmlrpc/2/object", allow_none=True)
    return models, uid

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Task 8 Odoo Deal Middleware"}

@app.post("/api/crm/deal", status_code=status.HTTP_201_CREATED)
def create_crm_deal(
    payload: DealPayload,
    x_api_key: str = Depends(verify_api_key),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    # 1. Kiểm tra Idempotency Key (chống duplicate request)
    if idempotency_key and idempotency_key in IDEMPOTENCY_CACHE:
        logger.info(f"⚡ [Idempotency] Trả về kết quả đã cache cho key: {idempotency_key}")
        return IDEMPOTENCY_CACHE[idempotency_key]

    full_name = f"{payload.firstname or ''} {payload.lastname or ''}".strip() or payload.deal_name
    phone = (payload.phone or "").strip()
    email = (payload.email or "").strip()

    models, uid = get_odoo_connection()

    try:
        # 2. Tìm hoặc Tạo/Cập nhật Contact (res.partner)
        partner_id = None
        partner_domain = []
        if phone:
            partner_domain = ['|', ('phone', '=', phone), ('mobile', '=', phone)]
        elif email:
            partner_domain = [('email', '=', email)]

        partner_vals = {
            'name': full_name,
            'phone': phone,
            'email': email,
        }

        if partner_domain:
            existing_partners = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'search', [partner_domain], {'limit': 1}
            )
            if existing_partners:
                partner_id = existing_partners[0]
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'write', [[partner_id], partner_vals]
                )
                logger.info(f"🔄 Đã cập nhật Contact Odoo (ID: {partner_id})")

        if not partner_id:
            partner_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'create', [partner_vals]
            )
            logger.info(f"✨ Đã tạo mới Contact Odoo (ID: {partner_id})")

        # 3. Tạo CRM Deal (crm.lead) và liên kết Contact
        deal_description = f"Nguồn: {payload.source} | Sự kiện: {payload.event}\nGhi chú: {payload.note}".strip()
        lead_payload = {
            'name': payload.deal_name,
            'partner_id': partner_id,
            'contact_name': full_name,
            'phone': phone,
            'email_from': email,
            'description': deal_description
        }

        deal_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead', 'create', [lead_payload]
        )
        logger.info(f"🎉 Tạo CRM Deal thành công (Deal ID: {deal_id}) liên kết Contact ID: {partner_id}")

        response_data = {
            "success": True,
            "deal_id": deal_id,
            "deal_name": payload.deal_name,
            "partner_id": partner_id,
            "partner_name": full_name,
            "message": "Contact and Deal created/associated successfully in Odoo"
        }

        # 4. Ghi Audit Log và lưu cache Idempotency
        if idempotency_key:
            IDEMPOTENCY_CACHE[idempotency_key] = response_data

        try:
            log_change(
                action="CREATE_DEAL_MIDDLEWARE",
                entity_type="crm.lead",
                entity_id=str(deal_id),
                source="Task 8 Middleware API",
                actor="External App",
                details_str=f"Created Deal '{payload.deal_name}' associated with Partner ID {partner_id}"
            )
        except Exception:
            pass

        return response_data

    except Exception as exc:
        logger.error(f"❌ Lỗi xử lý Middleware: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
