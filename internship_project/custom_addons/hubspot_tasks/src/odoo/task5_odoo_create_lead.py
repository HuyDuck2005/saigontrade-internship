import os
import logging
import xmlrpc.client
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task5_Odoo_Lead")

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo2_db")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

class OdooCRMClient:
    def __init__(self, url: str, db: str, user: str, password: str):
        self.url = url.rstrip('/')
        self.db = db
        self.user = user
        self.password = password
        self.uid = None

    def authenticate(self) -> int:
        try:
            common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)
            self.uid = common.authenticate(self.db, self.user, self.password, {})
            if not self.uid:
                raise ConnectionError("Xác thực thất bại: Sai Database, Username hoặc Password.")
            logger.info(f"✅ Đăng nhập Odoo thành công! (UID: {self.uid})")
            return self.uid
        except Exception as e:
            logger.error(f"❌ Lỗi kết nối Odoo: {e}")
            raise ConnectionError("Authentication or Connection failed")

    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        
        if not lead_data.get('name'):
            raise ValueError("Missing required field: 'name'")
    
        
        if not lead_data.get("name"):
            return {"success": False, "error": "Trường 'name' (Tên cơ hội/Lead) là bắt buộc."}
        
        if not self.uid:
            self.authenticate()

        models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)
        try:
            lead_id = models.execute_kw(
                self.db, self.uid, self.password,
                'crm.lead', 'create', [lead_data]
            )
            logger.info(f"🎉 Tạo CRM Lead thành công! Lead ID: {lead_id} - Title: '{lead_data.get('name')}'")
            return {"success": True, "lead_id": lead_id, "lead_name": lead_data.get('name'), "message": "Lead created successfully in Odoo"}
        except Exception as e:
            logger.error(f"❌ Không thể tạo Lead: {e}")
            return {"success": False, "error": str(e)}