from odoo import models, fields, api
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)

class SyncLog(models.Model):
    _name = 'sync.log'
    _description = 'Sync Log Monitoring Center'

    name = fields.Char(string='Log Reference', required=True, default='New')
    model_name = fields.Char(string='Model', required=True)
    record_id = fields.Integer(string='Record ID', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ], string='Status', default='pending', tracking=True)
    error_message = fields.Text(string='Error Message')
    retry_count = fields.Integer(string='Retry Count', default=0)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sync.log') or 'New'
        return super(SyncLog, self).create(vals)

    def action_retry(self):
        for log in self:
            if log.status == 'success':
                continue
            
            try:
                record = self.env[log.model_name].browse(log.record_id)
                if not record.exists():
                    log.write({'status': 'failed', 'error_message': 'Record no longer exists.'})
                    continue
                
                # Call specific sync methods if it's crm.lead or res.partner
                if log.model_name == 'crm.lead':
                    if hasattr(record, 'action_sync_deal_to_odoo2'):
                        record.action_sync_deal_to_odoo2()
                        log.write({'status': 'success', 'error_message': ''})
                elif log.model_name == 'res.partner':
                    if hasattr(record, 'action_sync_to_odoo2'):
                        record.action_sync_to_odoo2()
                        log.write({'status': 'success', 'error_message': ''})
                        
                log.retry_count += 1
            except Exception as e:
                log.write({'status': 'failed', 'error_message': str(e), 'retry_count': log.retry_count + 1})

    @api.model
    def cron_retry_failed_logs(self):
        failed_logs = self.search([('status', 'in', ['failed', 'pending']), ('retry_count', '<', 5)])
        for log in failed_logs:
            log.action_retry()
