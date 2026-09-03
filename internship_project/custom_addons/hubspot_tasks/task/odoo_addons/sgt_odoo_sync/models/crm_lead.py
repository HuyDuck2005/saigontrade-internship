from odoo import models, fields, api
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sync_status = fields.Selection([
        ('draft', 'Chưa đồng bộ'),
        ('success', 'Đồng bộ thành công'),
        ('failed', 'Đồng bộ thất bại')
    ], string='Trạng thái Sync Odoo 2', default='draft')

    remote_lead_id = fields.Integer(string='Remote Deal ID (Odoo 2)')
    remote_partner_id = fields.Integer(string='Remote Partner ID (Odoo 2)')
    sync_error_msg = fields.Text(string='Chi tiết lỗi Sync')
    retry_count = fields.Integer(string='Số lần Retry', default=0)

    def action_create_contact_both(self):
        """Task 6: Nút Tạo/Cập nhật Contact trên cả Odoo 1 và Odoo 2."""
        for lead in self:
            config = self.env['sgt.remote.odoo'].search([('is_active', '=', True)], limit=1)
            phone = lead.phone or lead.mobile
            if not phone:
                lead.write({'sync_status': 'failed', 'sync_error_msg': 'Thiếu số điện thoại'})
                continue

            # 1. Xử lý Odoo 1 (Local)
            partner = self.env['res.partner'].search([('phone', '=', phone)], limit=1)
            vals = {'name': lead.contact_name or lead.name, 'phone': phone, 'email': lead.email_from}
            if partner:
                partner.write(vals)
            else:
                partner = self.env['res.partner'].create(vals)
            lead.partner_id = partner.id

            # 2. Xử lý Odoo 2 (Remote)
            if config:
                try:
                    c = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/common", allow_none=True)
                    uid = c.authenticate(config.db, config.username, config.password, {})
                    m = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/object", allow_none=True)
                    
                    p2 = m.execute_kw(config.db, uid, config.password, 'res.partner', 'search', [[['phone', '=', phone]]])
                    if p2:
                        m.execute_kw(config.db, uid, config.password, 'res.partner', 'write', [p2, vals])
                        lead.write({'remote_partner_id': p2[0], 'sync_status': 'success', 'sync_error_msg': False})
                    else:
                        new_p2 = m.execute_kw(config.db, uid, config.password, 'res.partner', 'create', [vals])
                        lead.write({'remote_partner_id': new_p2, 'sync_status': 'success', 'sync_error_msg': False})
                except Exception as e:
                    lead.write({'sync_status': 'failed', 'sync_error_msg': str(e), 'retry_count': lead.retry_count + 1})
        return True

    def action_retry_sync(self):
        """Task 10: Nút Retry Sync Deal sang Odoo 2."""
        self.ensure_one()
        config = self.env['sgt.remote.odoo'].search([('is_active', '=', True)], limit=1)
        if not config:
            return
        try:
            c = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/common", allow_none=True)
            uid = c.authenticate(config.db, config.username, config.password, {})
            m = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/object", allow_none=True)

            remote_vals = {
                'name': self.name,
                'expected_revenue': self.expected_revenue,
                'x_deal_id': f"NL{self.id}"
            }
            if self.remote_lead_id:
                m.execute_kw(config.db, uid, config.password, 'crm.lead', 'write', [[self.remote_lead_id], remote_vals])
            else:
                rem_id = m.execute_kw(config.db, uid, config.password, 'crm.lead', 'create', [remote_vals])
                self.remote_lead_id = rem_id

            self.write({'sync_status': 'success', 'sync_error_msg': False})
        except Exception as e:
            self.write({'sync_status': 'failed', 'sync_error_msg': str(e), 'retry_count': self.retry_count + 1})
