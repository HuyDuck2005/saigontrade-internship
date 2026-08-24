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
        """TASK 10: Tự động hóa Dual-Write. Ghi đè hàm create để kích hoạt đồng bộ khi Deal vừa được tạo."""
        leads = super(CrmLead, self).create(vals_list)
        for lead in leads:
            # Kích hoạt đồng bộ Deal tự động
            lead.action_sync_deal_to_odoo2()
        return leads

    def action_sync_deal_to_odoo2(self):
        """Logic xử lý đồng bộ Deal sang Odoo 2, không làm Rollback Odoo 1 nếu Odoo 2 rớt mạng."""
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
                    'x_deal_id': f"NL{lead.id}"  # Đánh dấu ID gốc
                }
                
                if lead.remote_lead_id:
                    models2.execute_kw(config.db, uid2, config.password, 'crm.lead', 'write', [[lead.remote_lead_id], remote_vals])
                else:
                    remote_id = models2.execute_kw(config.db, uid2, config.password, 'crm.lead', 'create', [remote_vals])
                    lead.remote_lead_id = remote_id

                lead.write({
                    'sync_status': 'success',
                    'sync_error_msg': False
                })
            except Exception as e:
                _logger.warning(f"Dual-write Odoo 2 tạm thời thất bại: {e}")
                lead.write({
                    'sync_status': 'failed',
                    'sync_error_msg': str(e),
                    'retry_count': lead.retry_count + 1
                })

    def action_create_contact_both(self):
        """TASK 6 & 7: Đồng bộ Contact (Upsert) và Mapping Custom Fields."""
        for lead in self:
            config = self.env['sgt.remote.odoo'].search([('is_active', '=', True)], limit=1)
            phone = lead.phone or lead.mobile
            if not phone:
                lead.write({'sync_status': 'failed', 'sync_error_msg': 'Thiếu số điện thoại định danh'})
                continue

            # Ánh xạ trường cơ bản
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

            # TASK 7: Ánh xạ Custom Field động (Nếu có dữ liệu thì map, nếu không bỏ qua)
            custom_fields_map = {
                'x_firstname': 'x_custome_fields_firstname',
                'x_lastname': 'x_custome_fields_lastname',
                'x_jobtitle': 'x_custome_fields_jobtitle',
            }
            for local_f, remote_f in custom_fields_map.items():
                if hasattr(lead, local_f) and getattr(lead, local_f):
                    partner_vals[remote_f] = getattr(lead, local_f)

            # 1. Xử lý local Odoo 1
            partner = self.env['res.partner'].search([('phone', '=', phone)], limit=1)
            if partner:
                partner.write(partner_vals)
            else:
                partner = self.env['res.partner'].create(partner_vals)
            lead.partner_id = partner.id

            # 2. Xử lý remote Odoo 2
            if config:
                try:
                    c = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/common", allow_none=True)
                    uid = c.authenticate(config.db, config.username, config.password, {})
                    m = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/object", allow_none=True)

                    p2 = m.execute_kw(config.db, uid, config.password, 'res.partner', 'search', [[['phone', '=', phone]]])
                    
                    # Lọc bớt key rác có thể làm Odoo 2 crash nếu chưa tạo custom fields bên kia
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

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_retry_sync(self):
        """Nút Retry tổng: Chạy lại đồng bộ Contact và Deal."""
        self.action_create_contact_both()
        self.action_sync_deal_to_odoo2()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
