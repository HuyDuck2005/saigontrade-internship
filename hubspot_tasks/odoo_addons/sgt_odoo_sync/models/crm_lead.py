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

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(CrmLead, self).create(vals_list)
        for lead in leads:
            lead.action_sync_deal_to_odoo2()
        return leads

    def action_sync_deal_to_odoo2(self):
        for lead in self:
            config = self.env['sgt.remote.odoo'].search([('is_active', '=', True)], limit=1)
            if not config:
                continue
            try:
                common = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/common", allow_none=True)
                uid2 = common.authenticate(config.db, config.username, config.password, {})
                if not uid2:
                    raise ConnectionError("Remote Odoo 2 auth failed")

                models2 = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/object", allow_none=True)
                remote_vals = {
                    'name': lead.name,
                    'expected_revenue': lead.expected_revenue,
                    'type': 'opportunity',
                    'x_deal_id': f"NL{lead.id}" 
                }

                if lead.remote_lead_id:
                    models2.execute_kw(config.db, uid2, config.password, 'crm.lead', 'write', [[lead.remote_lead_id], remote_vals])
                else:
                    remote_id = models2.execute_kw(config.db, uid2, config.password, 'crm.lead', 'create', [remote_vals])
                    lead.remote_lead_id = remote_id

                lead.write({'sync_status': 'success', 'sync_error_msg': False})
            except Exception as e:
                _logger.warning(f"Dual-write Odoo 2 thất bại: {e}")
                lead.write({'sync_status': 'failed', 'sync_error_msg': str(e), 'retry_count': lead.retry_count + 1})

    def action_create_contact_both(self):
        for lead in self:
            config = self.env['sgt.remote.odoo'].search([('is_active', '=', True)], limit=1)
            phone = lead.phone or lead.mobile
            if not phone:
                lead.write({'sync_status': 'failed', 'sync_error_msg': 'Thiếu số điện thoại định danh'})
                continue

            # Ánh xạ cơ bản
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

            # 🌟 KIẾN TRÚC MỚI: DYNAMIC MAPPING & ROLE-BASED 
            mappings = self.env['sync.configuration'].search([
                ('model_id.model', '=', 'crm.lead'), 
                ('active', '=', True)
            ])
            
            for mapping in mappings:
                # Kiểm tra quyền: Bỏ qua nếu user không thuộc nhóm được cấp phép (Giải pháp 3)
                if mapping.security_group_ids and not any(group in self.env.user.groups_id for group in mapping.security_group_ids):
                    continue
                    
                local_f = mapping.field_id.name
                remote_f = mapping.remote_field_name
                
                if hasattr(lead, local_f) and getattr(lead, local_f):
                    partner_vals[remote_f] = getattr(lead, local_f)

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
                    safe_partner_vals = {k: v for k, v in partner_vals.items() if not k.startswith('x_') or hasattr(lead, k)}

                    if p2:
                        m.execute_kw(config.db, uid, config.password, 'res.partner', 'write', [p2, safe_partner_vals])
                        lead.write({'remote_partner_id': p2[0], 'sync_status': 'success', 'sync_error_msg': ''})
                    else:
                        new_p2 = m.execute_kw(config.db, uid, config.password, 'res.partner', 'create', [safe_partner_vals])
                        lead.write({'remote_partner_id': new_p2, 'sync_status': 'success', 'sync_error_msg': ''})
                except Exception as e:
                    lead.write({'sync_status': 'failed', 'sync_error_msg': f"Lỗi Contact Sync: {e}", 'retry_count': lead.retry_count + 1})
            else:
                lead.write({'sync_status': 'failed', 'sync_error_msg': 'Chưa cấu hình URL Odoo 2'})

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_retry_sync(self):
        self.action_create_contact_both()
        self.action_sync_deal_to_odoo2()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
