from odoo import models, fields, api
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)

class SgtRemoteOdoo(models.Model):
    _name = 'sgt.remote.odoo'
    _description = 'Cấu hình kết nối Odoo 2'

    name = fields.Char(string='Tên cấu hình', required=True, default='Odoo 2 Production')
    url = fields.Char(string='Odoo URL', required=True, default='http://localhost:8070')
    db = fields.Char(string='Database Name', required=True, default='odoo2_db')
    username = fields.Char(string='Username', required=True, default='admin')
    password = fields.Char(string='Password / API Key', required=True, default='admin')
    is_active = fields.Boolean(string='Đang kích hoạt', default=True)

    def test_connection(self):
        self.ensure_one()
        try:
            common = xmlrpc.client.ServerProxy(f"{self.url.rstrip('/')}/xmlrpc/2/common", allow_none=True)
            uid = common.authenticate(self.db, self.username, self.password, {})
            if uid:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Thành công',
                        'message': f'Kết nối Odoo 2 thành công! (UID: {uid})',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Thất bại',
                        'message': 'Sai thông tin đăng nhập hoặc Database.',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Lỗi kết nối',
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
