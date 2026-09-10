import os
import sys
import logging
import time

# Khai báo đường dẫn để import module task5
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from odoo.task5_odoo_create_lead import OdooCRMClient, ODOO_URL, ODOO_USERNAME, ODOO_PASSWORD

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task14_Queue")

# Ép kiểu dùng odoo_db (database đang chạy hiện tại của Odoo 1)
ODOO_DB_LOCAL = "odoo_db"

def process_queue():
    logger.info("🚀 BẮT ĐẦU QUÉT GOOGLE SHEET QUEUE...")
    client = OdooCRMClient("http://localhost:8069", ODOO_DB_LOCAL, ODOO_USERNAME, ODOO_PASSWORD)
    
    # Giả lập dữ liệu đọc từ Google Sheet bằng gspread.worksheet.get_all_records()
    sheet_rows = [
        {"row_idx": 2, "status": "NEW", "deal_name": "Đơn hàng từ Queue 1", "contact_name": "Trần A", "phone": "0911000111"},
        {"row_idx": 3, "status": "PROCESSING", "deal_name": "Đơn hàng đang kẹt", "contact_name": "Lê B", "phone": "0922000222"},
        {"row_idx": 4, "status": "NEW", "deal_name": "Đơn hàng từ Queue 2", "contact_name": "Phạm C", "phone": "0933000333"}
    ]
    
    logger.info(f"Đã tải {len(sheet_rows)} dòng từ Google Sheet.")
    
    for row in sheet_rows:
        status = row.get("status")
        row_idx = row.get("row_idx")
        
        if status != "NEW":
            logger.info(f"⏭️ Bỏ qua dòng {row_idx} (Trạng thái hiện tại: {status})")
            continue
            
        logger.info(f"⏳ Đang xử lý dòng {row_idx} - Đổi trạng thái Sheet thành PROCESSING...")
        # Ở môi trường thật: ws.update_cell(row_idx, col_status, 'PROCESSING')
        
        lead_data = {
            "name": row.get("deal_name"),
            "contact_name": row.get("contact_name"),
            "phone": row.get("phone")
        }
        
        try:
            res = client.create_lead(lead_data)
            if res.get("success"):
                logger.info(f"✅ THÀNH CÔNG! Dòng {row_idx} -> Đã tạo Odoo Deal ID: {res['lead_id']}")
                logger.info(f"🔄 Đổi trạng thái Sheet thành DONE.\n")
                # Ở môi trường thật: ws.update_cell(row_idx, col_status, 'DONE')
            else:
                logger.error(f"❌ Lỗi dòng {row_idx}: {res.get('error')}")
                logger.info(f"🔄 Đổi trạng thái Sheet thành ERROR.\n")
        except Exception as e:
            logger.error(f"❌ Exception tại dòng {row_idx}: {str(e)}")
            logger.info(f"🔄 Đổi trạng thái Sheet thành ERROR.\n")

if __name__ == "__main__":
    process_queue()
