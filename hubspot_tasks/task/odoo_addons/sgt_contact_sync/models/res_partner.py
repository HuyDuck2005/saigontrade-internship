import os
import logging
import xmlrpc.client
from odoo import models, fields, api
from odoo.exceptions import UserError

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
        
        # CHÌA KHÓA Ở ĐÂY: Trỏ sang Database mới tinh của Odoo 2
        ODOO2_DB = "odoo2_db" 
        ODOO2_USER = "admin"
        ODOO2_PASSWORD = "admin"

        try:
            common = xmlrpc.client.ServerProxy(f"{ODOO2_URL.rstrip('/')}/xmlrpc/2/common", allow_none=True)
            uid = common.authenticate(ODOO2_DB, ODOO2_USER, ODOO2_PASSWORD, {})
            
            if not uid:
                raise UserError(f"Sai tài khoản hoặc Database '{ODOO2_DB}' chưa được tạo bên Odoo 2!")

            models_proxy = xmlrpc.client.ServerProxy(f"{ODOO2_URL.rstrip('/')}/xmlrpc/2/object", allow_none=True)
            
            partner_vals = {
                'name': self.name,
                'phone': self.phone or '',
                'mobile': self.mobile or '',
                'email': self.email or '',
                'comment': f"Được đồng bộ tự động từ Odoo 1 sang Odoo 2 (Khác Database) lúc {fields.Datetime.now()}"
            }

            domain = []
            if self.email:
                domain = [('email', '=', self.email)]
            elif self.mobile:
                domain = [('mobile', '=', self.mobile)]
            elif self.phone:
                domain = [('phone', '=', self.phone)]

            existing = []
            if domain:
                existing = models_proxy.execute_kw(
                    ODOO2_DB, uid, ODOO2_PASSWORD, 'res.partner', 'search', 
                    [domain], {'limit': 1}
                )

            if existing:
                models_proxy.execute_kw(ODOO2_DB, uid, ODOO2_PASSWORD, 'res.partner', 'write', [[existing[0]], partner_vals])
            else:
                models_proxy.execute_kw(ODOO2_DB, uid, ODOO2_PASSWORD, 'res.partner', 'create', [partner_vals])

            self.write({'sync_status_odoo2': 'synced'})
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Đồng bộ Dữ liệu THẬT thành công',
                    'message': 'Đã đẩy dữ liệu xuyên qua 2 Database độc lập!',
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                }
            }

        except Exception as e:
            self.write({'sync_status_odoo2': 'failed'})
            raise UserError(f"Lỗi đồng bộ sang Odoo 2: {str(e)}")
