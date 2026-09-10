import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_hubspot_deal_id = fields.Char(string='HubSpot Deal ID', readonly=True)
    x_hubspot_sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ], string='HubSpot Sync Status', default='pending', readonly=True)
    x_hubspot_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    x_hubspot_sync_error = fields.Text(string='Sync Error', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(CrmLead, self).create(vals_list)
        # Kích hoạt đồng bộ ngay khi Deal được tạo
        for lead in leads:
            lead.action_sync_to_hubspot()
        return leads

    def action_sync_to_hubspot(self):
        for lead in self:
            try:
                _logger.info(f"🚀 [TASK 17] Đang đồng bộ Deal '{lead.name}' sang HubSpot...")
                
                # TODO: Tại đây sẽ gắn requests.post() gọi API v3 của HubSpot
                # Tạm thời giả lập phản hồi thành công từ API
                
                lead.write({
                    'x_hubspot_deal_id': f'HS_DEAL_{lead.id}',
                    'x_hubspot_sync_status': 'success',
                    'x_hubspot_sync_date': fields.Datetime.now(),
                    'x_hubspot_sync_error': False
                })
                _logger.info(f"✅ Đã đồng bộ thành công! HubSpot ID: HS_DEAL_{lead.id}")
            except Exception as e:
                lead.write({
                    'x_hubspot_sync_status': 'failed',
                    'x_hubspot_sync_error': str(e)
                })
                _logger.error(f"❌ Lỗi đồng bộ: {e}")
