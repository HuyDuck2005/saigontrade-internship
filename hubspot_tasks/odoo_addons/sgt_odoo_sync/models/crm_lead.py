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
        for lead in self:
            config = self.env['sgt.remote.odoo'].search([('is_active', '=', True)], limit=1)
            phone = lead.phone or lead.mobile
            if not phone:
                lead.write({'sync_status': 'failed', 'sync_error_msg': 'Thiếu số điện thoại'})
                continue

            # Mở rộng trường đồng bộ sang Odoo 2
            partner_vals = {
                'name': lead.contact_name or lead.partner_name or lead.name or 'Unknown',
                'phone': phone,
                'company_type': 'person',
                'function': lead.function or '',
                'mobile': lead.mobile or '',
                'website': lead.website or '',
            }
            if lead.email_from:
                partner_vals['email'] = lead.email_from

            # 1. Local Odoo 1
            partner = self.env['res.partner'].search([('phone', '=', phone)], limit=1)
            if partner:
                partner.write(partner_vals)
            else:
                partner = self.env['res.partner'].create(partner_vals)
            lead.partner_id = partner.id

            # 2. Remote Odoo 2
            if config:
                try:
                    c = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/common", allow_none=True)
                    uid = c.authenticate(config.db, config.username, config.password, {})
                    m = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/object", allow_none=True)

                    p2 = m.execute_kw(config.db, uid, config.password, 'res.partner', 'search', [[['phone', '=', phone]]])
                    if p2:
                        m.execute_kw(config.db, uid, config.password, 'res.partner', 'write', [p2, partner_vals])
                        lead.write({'remote_partner_id': p2[0], 'sync_status': 'success', 'sync_error_msg': ''})
                    else:
                        new_p2 = m.execute_kw(config.db, uid, config.password, 'res.partner', 'create', [partner_vals])
                        lead.write({'remote_partner_id': new_p2, 'sync_status': 'success', 'sync_error_msg': ''})
                except Exception as e:
                    lead.write({'sync_status': 'failed', 'sync_error_msg': str(e), 'retry_count': lead.retry_count + 1})
            else:
                lead.write({'sync_status': 'failed', 'sync_error_msg': 'Chưa cấu hình URL Odoo 2'})
                
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_retry_sync(self):
        for lead in self:
            config = self.env['sgt.remote.odoo'].search([('is_active', '=', True)], limit=1)
            if not config:
                lead.write({'sync_error_msg': 'Chưa cấu hình URL Odoo 2'})
                continue
            try:
                c = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/common", allow_none=True)
                uid = c.authenticate(config.db, config.username, config.password, {})
                m = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/object", allow_none=True)

                remote_vals = {
                    'name': lead.name,
                    'expected_revenue': lead.expected_revenue,
                }
                
                if lead.remote_lead_id:
                    m.execute_kw(config.db, uid, config.password, 'crm.lead', 'write', [[lead.remote_lead_id], remote_vals])
                else:
                    rem_id = m.execute_kw(config.db, uid, config.password, 'crm.lead', 'create', [remote_vals])
                    lead.remote_lead_id = rem_id

                lead.write({'sync_status': 'success', 'sync_error_msg': ''})
            except Exception as e:
                lead.write({'sync_status': 'failed', 'sync_error_msg': str(e), 'retry_count': lead.retry_count + 1})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
