from odoo import models, fields, api
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sync_status = fields.Selection([
        ('draft', 'Draft'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ], string='Sync Status', default='draft')

    remote_partner_id = fields.Integer(string='Remote Partner ID')
    sync_error_msg = fields.Text(string='Sync Error')
    retry_count = fields.Integer(string='Retry Count', default=0)

    def action_sync_to_odoo2(self):
        for partner in self:
            config = self.env['sgt.remote.odoo'].search([('is_active', '=', True)], limit=1)
            if not config:
                partner.write({'sync_status': 'failed', 'sync_error_msg': 'Odoo 2 Config not found.'})
                continue
            
            try:
                c = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/common", allow_none=True)
                uid = c.authenticate(config.db, config.username, config.password, {})
                m = xmlrpc.client.ServerProxy(f"{config.url}/xmlrpc/2/object", allow_none=True)
                
                search_domain = []
                if partner.email:
                    search_domain = [['email', '=', partner.email]]
                elif partner.phone:
                    search_domain = [['phone', '=', partner.phone]]
                
                partner_vals = {
                    'name': partner.name,
                    'email': partner.email or '',
                    'phone': partner.phone or '',
                }

                if search_domain:
                    remote_partner = m.execute_kw(config.db, uid, config.password, 'res.partner', 'search', [search_domain])
                    if remote_partner:
                        m.execute_kw(config.db, uid, config.password, 'res.partner', 'write', [remote_partner, partner_vals])
                        partner.write({'remote_partner_id': remote_partner[0], 'sync_status': 'success', 'sync_error_msg': ''})
                    else:
                        new_id = m.execute_kw(config.db, uid, config.password, 'res.partner', 'create', [partner_vals])
                        partner.write({'remote_partner_id': new_id, 'sync_status': 'success', 'sync_error_msg': ''})
                else:
                    new_id = m.execute_kw(config.db, uid, config.password, 'res.partner', 'create', [partner_vals])
                    partner.write({'remote_partner_id': new_id, 'sync_status': 'success', 'sync_error_msg': ''})
            except Exception as e:
                partner.write({'sync_status': 'failed', 'sync_error_msg': str(e), 'retry_count': partner.retry_count + 1})

