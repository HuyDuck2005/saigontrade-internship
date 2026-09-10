from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    x_social_platform = fields.Selection([('facebook', 'Facebook'), ('tiktok', 'TikTok')], string='Social Platform')
    x_social_profile_name = fields.Char(string='Profile Name')
    x_social_profile_url = fields.Char(string='Profile URL')
    x_social_post_text = fields.Text(string='Social Post Text')
