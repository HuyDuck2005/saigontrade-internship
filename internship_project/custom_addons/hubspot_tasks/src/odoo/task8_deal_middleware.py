import os
import sys
import xmlrpc.client
import logging
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, status, Depends
from pydantic import BaseModel, Field

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.audit_logger import log_change

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task8_Middleware_Advanced")

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo2_db")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")
API_MIDDLEWARE_KEY = os.getenv("API_MIDDLEWARE_KEY", "sgt_secret_api_key_2026")

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
    expected_revenue: Optional[float] = 0.0
    currency: Optional[str] = "VND"  # Hỗ trợ đa tiền tệ (Lỗi 4)

app = FastAPI(title="SGT Odoo Deal Middleware Advanced API", version="2.0")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key != API_MIDDLEWARE_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing X-API-Key header")
    return x_api_key

def get_odoo_connection():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL.rstrip('/')}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise HTTPException(status_code=500, detail="Không thể kết nối / xác thực Odoo CRM")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL.rstrip('/')}/xmlrpc/2/object", allow_none=True)
    return models, uid

def normalize_phone(phone_str: str) -> str:
    if not phone_str: return ""
    p = re.sub(r'[^\d+]', '', phone_str)
    if p.startswith('+84'): p = '0' + p[3:]
    elif p.startswith('84') and len(p) > 9: p = '0' + p[2:]
    return p

@app.post("/api/crm/deal", status_code=status.HTTP_201_CREATED)
def create_crm_deal(
    payload: DealPayload,
    x_api_key: str = Depends(verify_api_key),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    if idempotency_key and idempotency_key in IDEMPOTENCY_CACHE:
        logger.info(f"⚡ [Idempotency] Trả về cache cho key: {idempotency_key}")
        return IDEMPOTENCY_CACHE[idempotency_key]

    full_name = f"{payload.firstname or ''} {payload.lastname or ''}".strip() or payload.deal_name
    phone = normalize_phone(payload.phone)
    email = (payload.email or "").strip()

    models, uid = get_odoo_connection()

    try:
        partner_id = None
        partner_domain = []
        if phone:
            partner_domain = ['|', ('phone', '=', phone), ('phone', '=', phone)]
        elif email:
            partner_domain = [('email', '=', email)]

        if partner_domain:
            existing_partners = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'search', [partner_domain], {'limit': 1})
            if existing_partners:
                partner_id = existing_partners[0]
                
                # NGHIỆP VỤ MỚI (LỖI 3 - NON-DESTRUCTIVE UPDATE):
                # Chỉ cập nhật các trường có giá trị truyền lên, KHÔNG ghi đè dữ liệu cũ bằng chuỗi rỗng
                current_partner_data = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'read', [partner_id], {'fields': ['name', 'phone', 'email']})[0]
                update_vals = {}
                if full_name and current_partner_data.get('name') in [False, '', 'Client']:
                    update_vals['name'] = full_name
                if phone and not current_partner_data.get('phone'):
                    update_vals['phone'] = phone
                if email and not current_partner_data.get('email'):
                    update_vals['email'] = email
                
                if update_vals:
                    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'write', [[partner_id], update_vals])

        # Nếu chưa có thì tạo mới Partner
        if not partner_id:
            partner_vals = {
                'name': full_name,
                'phone': phone,
                'email': email,
            }
            partner_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'create', [partner_vals])

        # NGHIỆP VỤ MỚI (LỖI 4 - MULTI-CURRENCY CONVERSION):
        # Giả lập quy đổi tỷ giá ngoại tệ sang VND nếu payload gửi lên bằng USD
        revenue = payload.expected_revenue or 0.0
        currency_code = payload.currency.upper() if payload.currency else "VND"
        if currency_code == "USD":
            revenue = revenue * 25400 # Tỷ giá quy đổi giả định tiêu chuẩn

        deal_description = f"Nguồn: {payload.source} | Sự kiện: {payload.event} | Tiền tệ gốc: {currency_code}\nGhi chú: {payload.note}".strip()
        lead_payload = {
            'name': payload.deal_name,
            'partner_id': partner_id,
            'contact_name': full_name,
            'phone': phone,
            'email_from': email,
            'expected_revenue': revenue,
            'description': deal_description
        }

        deal_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.lead', 'create', [lead_payload])

        response_data = {
            "success": True,
            "deal_id": deal_id,
            "deal_name": payload.deal_name,
            "partner_id": partner_id,
            "partner_name": full_name,
            "converted_revenue_vnd": revenue,
            "message": "Contact and Deal processed successfully with Advanced Business Rules"
        }

        if idempotency_key:
            IDEMPOTENCY_CACHE[idempotency_key] = response_data

        return response_data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

class AttachmentPayload(BaseModel):
    deal_id: int = Field(..., description="ID ca CRM Deal")
    filename: str = Field(..., description="TAn file A-nh kA?m")
    image_base64: str = Field(..., description="NTi dung file dng base64")
    mime_type: str = Field(..., description="MIME type (image/png, image/jpeg, application/pdf)")

@app.post("/api/crm/attachment", status_code=status.HTTP_201_CREATED)
def upload_crm_attachment(
    payload: AttachmentPayload,
    x_api_key: str = Depends(verify_api_key)
):
    if payload.mime_type not in ["image/png", "image/jpeg", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid MIME type. Only png, jpeg, and pdf are allowed.")
    
    size_in_bytes = (len(payload.image_base64) * 3) / 4
    if payload.image_base64.endswith('=='):
        size_in_bytes -= 2
    elif payload.image_base64.endswith('='):
        size_in_bytes -= 1
        
    if size_in_bytes > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
        
    models, uid = get_odoo_connection()
    
    try:
        attachment_vals = {
            'name': payload.filename,
            'type': 'binary',
            'datas': payload.image_base64,
            'res_model': 'crm.lead',
            'res_id': payload.deal_id,
            'mimetype': payload.mime_type,
        }
        
        attachment_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.attachment', 'create', [attachment_vals])
        
        return {
            "success": True,
            "attachment_id": attachment_id,
            "message": "Attachment uploaded and linked to Deal successfully."
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
