import logging
import threading
from odoo import models, api

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        # 1. Vẫn tạo Deal bình thường
        leads = super(CrmLead, self).create(vals_list)
        
        # 2. Đẩy tác vụ gọi Google Sheets sang một luồng ngầm (Background Thread)
        for lead in leads:
            thread = threading.Thread(
                target=self._async_log_to_sheet, 
                args=(lead.id, lead.name, lead.expected_revenue, lead.email_from)
            )
            thread.start()
            
        return leads

    def _async_log_to_sheet(self, lead_id, name, amount, email):
        """Hàm này chạy độc lập, nếu có lỗi mạng cũng không làm Odoo bị crash"""
        try:
            # TODO: Ở môi trường thật sẽ dùng gspread hoặc requests gọi webhook Google App Script ở đây
            _logger.info(f"✅ [TASK 13] Đang đẩy thành công lên Google Sheet -> Deal ID: {lead_id} | Tên: {name} | Revenue: {amount} | Email: {email}")
            
            # Giả lập phát sinh lỗi kết nối để test khả năng chịu lỗi
            # raise ConnectionError("Google API Timeout!")
            
        except Exception as e:
            # Lỗi sẽ được ghi vào file log của Odoo (hoặc Sheet "Errors") thay vì đập vào mặt người dùng
            _logger.error(f"❌ [TASK 13] Lỗi khi đồng bộ Google Sheet cho Deal {lead_id}: {e}")
