from odoo import models, fields

class LeadApprovalHistory(models.Model):
    _name = 'lead.approval.history'
    _description = 'Lịch sử duyệt Lead'
    _order = 'create_date desc'
    
    lead_id = fields.Many2one('crm.lead', string="Lead", required=True)
    action = fields.Selection([
        ('submitted', 'Submit'),
        ('approved', 'Phê duyệt'),
        ('rejected', 'Từ chối'),
        ('resubmitted', 'Gửi lại'),
    ], string="Hành động", required=True)
    
    performed_by = fields.Many2one('res.users', string="Người thực hiện", default=lambda self: self.env.user.id)
    notes = fields.Text(string="Ghi chú")
