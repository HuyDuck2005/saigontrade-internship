import os
import logging
import socket
import xmlrpc.client
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger("Task5_Odoo_Lead")

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo_db")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")
SOCKET_TIMEOUT = 15

class OdooCRMClient:
    def __init__(self, url: str, db: str, user: str, password: str):
        self.url = url.rstrip('/')
        self.db = db
        self.user = user
        self.password = password
        self.uid = None

    def authenticate(self) -> int:
        socket.setdefaulttimeout(SOCKET_TIMEOUT)
        try:
            common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)
            uid = common.authenticate(self.db, self.user, self.password, {})
            if not uid:
                logger.error("❌ Xác thực thất bại: Sai Database, Username hoặc Password.")
                return 0
            self.uid = uid
            logger.info(f"✅ Đăng nhập Odoo thành công! (UID: {self.uid})")
            return self.uid
        except (socket.timeout, TimeoutError):
            logger.error("❌ Lỗi: Timeout khi kết nối tới máy chủ Odoo.")
            return 0
        except (ConnectionRefusedError, ConnectionError):
            logger.error("❌ Lỗi: Không thể kết nối tới máy chủ Odoo (Connection Refused).")
            return 0
        except Exception as e:
            logger.error(f"❌ Lỗi xác thực Odoo: {e}")
            return 0

    def create_lead(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("name"):
            raise ValueError("Trường 'name' (Tên cơ hội/Lead) là bắt buộc.")

        if not self.uid:
            self.authenticate()
            if not self.uid:
                return {"success": False, "error": "Authentication or Connection failed"}

        lead_payload = {
            "name": data.get("name"),
            "contact_name": data.get("contact_name") or "",
            "phone": data.get("phone") or "",
            "email_from": data.get("email") or "",
            "description": f"Sự kiện: {data.get('event', '')} | Địa điểm: {data.get('event_location', '')}\n{data.get('description', '')}".strip()
        }

        try:
            models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)
            lead_id = models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'crm.lead',
                'create',
                [lead_payload]
            )
            logger.info(f"🎉 Tạo CRM Lead thành công! Lead ID: {lead_id} - Title: '{data.get('name')}'")
            return {
                "success": True,
                "lead_id": lead_id,
                "lead_name": data.get("name"),
                "message": "Lead created successfully in Odoo"
            }
        except xmlrpc.client.Fault as fault:
            logger.error(f"❌ Lỗi Odoo XML-RPC: {fault.faultString}")
            return {"success": False, "error": fault.faultString}
        except Exception as e:
            logger.error(f"❌ Lỗi tạo Lead: {e}")
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    client = OdooCRMClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
    test_lead = {
        "name": "Cơ hội khách hàng đối tác - SGT Expo 2026",
        "contact_name": "Nguyen Van C",
        "phone": "0912345678",
        "email": "nguyenvanc@example.com",
        "event": "SGT Expo 2026",
        "event_location": "TP. Hồ Chí Minh",
        "description": "Khách hàng quan tâm giải pháp CRM Odoo."
    }
    res = client.create_lead(test_lead)
    print("Kết quả:", res)
