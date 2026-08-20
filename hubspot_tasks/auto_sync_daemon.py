import time
import logging
from task1_hubspot_to_sheet import sync_contacts
from task2_sheet_to_hubspot import import_contacts_from_sheet
from task3_deal_to_sheet import sync_deals

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("AutoSyncDaemon")

def run_all_tasks():
    logger.info("============== BẮT ĐẦU CHU KỲ ĐỒNG BỘ TỰ ĐỘNG ==============")
    try:
        logger.info("1. Đang kiểm tra Sheet -> HubSpot (Task 2)...")
        import_contacts_from_sheet()
        
        logger.info("2. Đang kiểm tra HubSpot -> Sheet (Task 1 Incremental)...")
        sync_contacts()
        
        logger.info("3. Đang cập nhật Deals & Summary (Task 3)...")
        sync_deals()
    except Exception as e:
        logger.error(f"Lỗi trong chu kỳ đồng bộ: {e}")
    logger.info("============== HOÀN TẤT CHU KỲ. NGHỈ 15 GIÂY ==============\n")

if __name__ == "__main__":
    logger.info("🚀 KHỞI ĐỘNG AUTO SYNC DAEMON (Nhấn Ctrl + C để dừng)...")
    while True:
        run_all_tasks()
        time.sleep(15)
