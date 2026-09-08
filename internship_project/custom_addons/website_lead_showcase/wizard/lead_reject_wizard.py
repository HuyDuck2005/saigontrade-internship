from odoo import models, fields

class LeadRejectWizard(models.TransientModel):
    _name = 'lead.reject.wizard'
    _description = 'Wizard Nhập lý do từ chối Lead'

    lead_id = fields.Many2one('crm.lead', string="Lead", required=True)
    rejection_reason = fields.Text(string="Lý do từ chối", required=True)

    def action_confirm_reject(self):
        self.lead_id.write({
            'approval_status': 'rejected',
            'website_visible': False,
            'rejection_reason': self.rejection_reason
        })
        self.env['lead.approval.history'].create({
            'lead_id': self.lead_id.id,
            'action': 'rejected',
            'performed_by': self.env.user.id,
            'notes': f'Lead bị từ chối: {self.rejection_reason}',
        })
        # Gửi email từ chối
        template = self.env.ref('website_lead_showcase.email_lead_rejected', raise_if_not_found=False)
        if template:
            template.send_mail(self.lead_id.id, force_send=True)
