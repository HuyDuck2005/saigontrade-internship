import os
import sys
import logging
import requests
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task16_HubSpot_To_Odoo")

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo_db")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

def get_odoo_connection():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise ConnectionError("Kết nối Odoo thất bại")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    return models, uid

def ensure_hubspot_custom_field(models, uid):
    fields = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "fields_get", [], {"attributes": ["string"]})
    if "x_hubspot_contact_id" not in fields:
        model_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "ir.model", "search", [[["model", "=", "res.partner"]]])
        if model_ids:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "ir.model.fields", "create", [{
                "name": "x_hubspot_contact_id",
                "model_id": model_ids[0],
                "ttype": "char",
                "field_description": "HubSpot Contact ID",
                "state": "manual"
            }])
            logger.info("✨ Đã tạo custom field x_hubspot_contact_id trên res.partner Odoo")

def fetch_hubspot_contacts_real(limit=50):
    if not HUBSPOT_TOKEN:
        logger.error("❌ Thiếu HUBSPOT_ACCESS_TOKEN trong file .env!")
        return []
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
    params = {"limit": limit, "properties": "firstname,lastname,email,phone,mobilephone,company,jobtitle"}
    res = requests.get(url, headers=headers, params=params, timeout=15)
    if res.status_code == 200:
        return res.json().get("results", [])
    logger.error(f"Lỗi gọi HubSpot API ({res.status_code}): {res.text}")
    return []

def sync_hubspot_to_odoo_real():
    models, uid = get_odoo_connection()
    ensure_hubspot_custom_field(models, uid)

    contacts = fetch_hubspot_contacts_real()
    logger.info(f"📥 Lấy được {len(contacts)} contacts thật từ HubSpot API v3.")

    created, updated = 0, 0
    for c in contacts:
        hs_id = str(c.get("id"))
        p = c.get("properties", {})
        firstname = p.get("firstname") or ""
        lastname = p.get("lastname") or ""
        full_name = f"{firstname} {lastname}".strip() or p.get("email") or f"HubSpot Contact {hs_id}"
        email = (p.get("email") or "").strip()
        phone = (p.get("phone") or p.get("mobilephone") or "").strip()

        # QUY TẮC ĐỐI SOÁT CHỐNG DUPLICATE
        matched_partner_id = None

        # 1. Tìm theo HubSpot ID
        p_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "search", [[["x_hubspot_contact_id", "=", hs_id]]], {"limit": 1})
        if p_ids:
            matched_partner_id = p_ids[0]

        # 2. Tìm theo Email
        if not matched_partner_id and email:
            p_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "search", [[["email", "=", email]]], {"limit": 1})
            if p_ids:
                matched_partner_id = p_ids[0]

        # 3. Tìm theo Phone
        if not matched_partner_id and phone:
            p_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "search", [[["phone", "=", phone]]], {"limit": 1})
            if p_ids:
                matched_partner_id = p_ids[0]

        vals = {
            "name": full_name,
            "email": email,
            "phone": phone,
            "function": p.get("jobtitle") or "",
            "x_hubspot_contact_id": hs_id
        }

        if matched_partner_id:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "write", [[matched_partner_id], vals])
            updated += 1
        else:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "create", [vals])
            created += 1

    logger.info(f"✅ TỔNG KẾT TASK 16: Tạo mới {created} Contact | Cập nhật {updated} Contact vào Odoo CRM.")

if __name__ == "__main__":
    sync_hubspot_to_odoo_real()
