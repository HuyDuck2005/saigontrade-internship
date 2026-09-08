from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CrmLeadApproval(models.Model):
    _inherit = 'crm.lead'

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Approval State', default='draft', tracking=True)

    discount_percentage = fields.Float(string='Discount (%)')

    def action_confirm_deal(self):
        for lead in self:
            # Check thresholds: e.g. discount > 10% or revenue > 1,000,000,000
            if lead.discount_percentage > 10.0 or lead.expected_revenue > 1000000000:
                if lead.approval_state != 'approved':
                    lead.write({'approval_state': 'pending'})
                    raise ValidationError("This deal exceeds the allowed discount or amount threshold. It requires Manager approval before confirmation.")
            
            # Additional confirmation logic can go here
            # For demonstration, setting to won/confirmed
            lead.action_set_won()
            
    def action_approve_deal(self):
        # In practice, limit this to groups="sales_team.group_sale_manager" in view
        self.write({'approval_state': 'approved'})

    def action_reject_deal(self):
        self.write({'approval_state': 'rejected'})
