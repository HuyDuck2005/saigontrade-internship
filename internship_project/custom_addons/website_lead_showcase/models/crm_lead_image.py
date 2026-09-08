from odoo import models, fields

class LeadImage(models.Model):
    _name = 'lead.image'
    _description = 'Thư viện ảnh Lead'
    
    lead_id = fields.Many2one('crm.lead', string='Lead', ondelete='cascade')
    image = fields.Image('Ảnh', required=True)
    name = fields.Char('Mô tả ảnh')

class CrmLeadImageExtension(models.Model):
    _inherit = 'crm.lead'
    
    image_ids = fields.One2many('lead.image', 'lead_id', string='Thư viện ảnh chi tiết')
