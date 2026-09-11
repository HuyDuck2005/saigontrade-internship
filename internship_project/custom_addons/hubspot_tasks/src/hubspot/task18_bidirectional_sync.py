import os
import sys
import logging
from datetime import datetime
import requests
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task18_Bidirectional_Sync")

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo_db")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

def get_odoo_client():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    return models, uid

def run_bidirectional_sync():
    logger.info("🔄 KHỞI CHẠY ĐỒNG BỘ HAI CHIỀU (HUBSPOT <-> ODOO) VỚI CƠ CHẾ CHỐNG LẶP VÒNG (LOOP PREVENTION)...")
    models, uid = get_odoo_client()
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}

    # CHIỀU 1: HubSpot -> Odoo
    url_hs = "https://api.hubapi.com/crm/v3/objects/contacts"
    res = requests.get(url_hs, headers=headers, params={"limit": 20, "properties": "firstname,lastname,email,phone,hs_lastmodifieddate"})
    if res.status_code == 200:
        for c in res.json().get("results", []):
            hs_id = str(c["id"])
            p = c.get("properties", {})
            email = (p.get("email") or "").strip()
            phone = (p.get("phone") or "").strip()
            name = f"{p.get('firstname') or ''} {p.get('lastname') or ''}".strip() or email

            # Tìm partner trên Odoo
            domain = ["|", ("x_hubspot_contact_id", "=", hs_id), ("email", "=", email)] if email else [("x_hubspot_contact_id", "=", hs_id)]
            partners = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "search_read", [domain], {"fields": ["id", "name", "write_date", "x_hubspot_contact_id"]})

            if partners:
                p_curr = partners[0]
                # CHỐNG LOOP: Nếu đã khớp ID và tên không đổi thì bỏ qua không ghi đè ngược lại
                if p_curr.get("x_hubspot_contact_id") == hs_id and p_curr.get("name") == name:
                    continue
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "write", [[p_curr["id"]], {"name": name, "x_hubspot_contact_id": hs_id}])
                logger.info(f"🔄 [HS -> Odoo] Cập nhật Contact ID {p_curr['id']} từ HubSpot {hs_id}")
            else:
                new_pid = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "create", [{"name": name, "email": email, "phone": phone, "x_hubspot_contact_id": hs_id}])
                logger.info(f"✨ [HS -> Odoo] Tạo mới Contact ID {new_pid} từ HubSpot {hs_id}")

    # CHIỀU 2: Odoo -> HubSpot (Chỉ đồng bộ các contact chưa có x_hubspot_contact_id)
    new_local_partners = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "res.partner", "search_read",
        [[["x_hubspot_contact_id", "=", False], ["email", "!=", False]]],
        {"fields": ["id", "name", "email", "phone"], "limit": 10}
    )

    for lp in new_local_partners:
        p_id = lp["id"]
        email = lp["email"]
        name = lp["name"] or ""
        parts = name.split(" ", 1)
        fname = parts[0]
        lname = parts[1] if len(parts) > 1 else ""

        # Gọi HubSpot tạo Contact
        payload = {"properties": {"email": email, "firstname": fname, "lastname": lname, "phone": lp.get("phone") or ""}}
        h_res = requests.post("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, json=payload)
        if h_res.status_code in [200, 201]:
            new_hs_id = h_res.json().get("id")
            # Cập nhật ngược lại ID vào Odoo để chặn vòng lặp lặp lại lần sau
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "write", [[p_id], {"x_hubspot_contact_id": str(new_hs_id)}])
            logger.info(f"🚀 [Odoo -> HS] Đẩy thành công Contact {p_id} sang HubSpot (HS ID: {new_hs_id})")
        elif h_res.status_code == 409:
            # Xung đột (Conflict): Contact đã có trên HubSpot, lấy ID gán ngược lại Odoo để giải quyết xung đột
            err_msg = h_res.json().get("message", "")
            if "Existing ID:" in err_msg:
                existing_id = err_msg.split("Existing ID:")[1].strip().split(" ")[0]
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "write", [[p_id], {"x_hubspot_contact_id": str(existing_id)}])
                logger.info(f"🛡️ [Conflict Solved] Gán liên kết Contact {p_id} với HubSpot ID hiện hữu: {existing_id}")

    logger.info("🎉 HOÀN THÀNH CHU KỲ ĐỒNG BỘ HAI CHIỀU AN TOÀN!")

if __name__ == "__main__":
    run_bidirectional_sync()
