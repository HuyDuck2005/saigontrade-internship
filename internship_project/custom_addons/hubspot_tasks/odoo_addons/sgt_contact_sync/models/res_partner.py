import logging
import xmlrpc.client
from odoo import models, fields

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sync_status_odoo2 = fields.Selection([
        ('draft', 'Chưa đồng bộ'),
        ('synced', 'Đồng bộ thành công'),
        ('failed', 'Đồng bộ thất bại')
    ], string='Trạng thái Sync Odoo 2', default='draft', readonly=True)

    def action_sync_to_odoo2(self):
        self.ensure_one()
        ODOO2_URL = "http://odoo2-app:8069"
        ODOO2_DB = "odoo_db"
        ODOO2_USER = "admin"
        ODOO2_PASSWORD = "admin"

        try:
            common = xmlrpc.client.ServerProxy(f"{ODOO2_URL}/xmlrpc/2/common", allow_none=True)
            uid = common.authenticate(ODOO2_DB, ODOO2_USER, ODOO2_PASSWORD, {})
            if uid:
                _logger.info("Đã kết nối Odoo 2 thành công để đồng bộ Contact.")
        except Exception as e:
            _logger.error(f"Lỗi đồng bộ: {e}")
