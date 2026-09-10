import os
import sys
import logging
import xmlrpc.client
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from odoo.task5_odoo_create_lead import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task16_HubSpot_Odoo_Sync")

# Giả lập database Odoo 1
ODOO_DB_LOCAL = "odoo_db"

def mock_hubspot_api_incremental(last_sync_time):
    """
    Giả lập API HubSpot với YÊU CẦU NÂNG CAO: Incremental Sync.
    Chỉ trả về những Contact có lastmodifieddate > last_sync_time.
    """
    logger.info(f"🔍 [Advanced] Đang gọi HubSpot API lấy các Contact thay đổi từ sau: {last_sync_time}")
    return [
        # Case 1: Tồn tại HubSpot ID -> Phải Update
        {"hs_id": "HS001", "firstname": "Nguyễn", "lastname": "Văn A", "email": "a@sgt.vn", "phone": "0911"},
        # Case 2: Không có HS ID, nhưng trùng Email -> Phải Update và gán HS ID
        {"hs_id": "HS002", "firstname": "Trần", "lastname": "Thị B", "email": "b@sgt.vn", "phone": "0922"},
        # Case 3: Không trùng ID, không trùng Email, trùng Phone -> Phải Update
        {"hs_id": "HS003", "firstname": "Lê", "lastname": "Văn C", "email": "c_new@sgt.vn", "phone": "0933"},
        # Case 4: Hoàn toàn mới -> Create
        {"hs_id": "HS004", "firstname": "Phạm", "lastname": "Đại D", "email": "d@sgt.vn", "phone": "0944"}
    ]

def get_odoo_models():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB_LOCAL, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    return models, uid

def ensure_hubspot_id_field(models, uid):
    """Tự động tạo custom field x_hubspot_contact_id nếu chưa có"""
    fields = models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'fields_get', [], {'attributes': ['string']})
    if 'x_hubspot_contact_id' not in fields:
        model_ids = models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'ir.model', 'search', [[['model', '=', 'res.partner']]])
        models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'ir.model.fields', 'create', [{
            'name': 'x_hubspot_contact_id', 'model_id': model_ids[0], 'ttype': 'char', 'field_description': 'HubSpot ID', 'state': 'manual'
        }])
        logger.info("✨ Đã tạo custom field 'x_hubspot_contact_id' trên Odoo.")

def run_sync():
    models, uid = get_odoo_models()
    ensure_hubspot_id_field(models, uid)
    
    # Giả lập thời gian chạy lần cuối (Incremental Sync)
    last_sync = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    hs_contacts = mock_hubspot_api_incremental(last_sync)
    
    # Khởi tạo dữ liệu mồi (Mock data) cho các Case 1, 2, 3 trong Odoo để test update
    models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'create', [{'name': 'Cũ A', 'x_hubspot_contact_id': 'HS001'}])
    models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'create', [{'name': 'Cũ B', 'email': 'b@sgt.vn'}])
    models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'create', [{'name': 'Cũ C', 'phone': '0933'}])
    
    for c in hs_contacts:
        hs_id = c['hs_id']
        email = c['email']
        phone = c['phone']
        full_name = f"{c['firstname']} {c['lastname']}"
        
        partner_id = None
        match_reason = ""
        
        # LOGIC ƯU TIÊN MATCHING
        # Ưu tiên 1: HubSpot ID
        p_ids = models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'search', [[['x_hubspot_contact_id', '=', hs_id]]])
        if p_ids:
            partner_id = p_ids[0]
            match_reason = "HubSpot ID"
        
        # Ưu tiên 2: Email
        if not partner_id and email:
            p_ids = models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'search', [[['email', '=', email]]])
            if p_ids:
                partner_id = p_ids[0]
                match_reason = "Email"
                
        # Ưu tiên 3: Phone
        if not partner_id and phone:
            p_ids = models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'search', [[['phone', '=', phone]]])
            if p_ids:
                partner_id = p_ids[0]
                match_reason = "Phone"
                
        # Xử lý Create hoặc Update
        vals = {
            'name': full_name,
            'email': email,
            'phone': phone,
            'x_hubspot_contact_id': hs_id
        }
        
        if partner_id:
            models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'write', [[partner_id], vals])
            logger.info(f"🔄 Đã UPDATE Contact '{full_name}' (Khớp bằng: {match_reason})")
        else:
            new_id = models.execute_kw(ODOO_DB_LOCAL, uid, ODOO_PASSWORD, 'res.partner', 'create', [vals])
            logger.info(f"✅ Đã CREATE Contact mới '{full_name}' (ID: {new_id})")

if __name__ == "__main__":
    run_sync()
