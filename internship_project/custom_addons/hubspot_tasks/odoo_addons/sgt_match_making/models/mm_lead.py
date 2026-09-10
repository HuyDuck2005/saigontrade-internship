from odoo import models, fields, api

class MatchMakingLead(models.Model):
    _name = 'mm.lead'
    _description = 'Match Making Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Match Reference', required=True, copy=False, readonly=True, default='New')
    
    partner_id = fields.Many2one('res.partner', string='Company A (Requestor)', required=True, tracking=True)
    partner_id_2 = fields.Many2one('res.partner', string='Company B (Target)', required=True, tracking=True)
    
    email_1 = fields.Char(related='partner_id.email', string='Email A', readonly=True)
    phone_1 = fields.Char(related='partner_id.phone', string='Phone A', readonly=True)
    email_2 = fields.Char(related='partner_id_2.email', string='Email B', readonly=True)
    phone_2 = fields.Char(related='partner_id_2.phone', string='Phone B', readonly=True)
    
    stage_id = fields.Selection([
        ('new', 'New Request'),
        ('qualified', 'Qualified'),
        ('proposition', 'Proposition / Intro'),
        ('won', 'Matched Successfully'),
        ('lost', 'Failed to Match')
    ], string='Stage', default='new', tracking=True, group_expand='_read_group_stage_ids')
    
    user_id = fields.Many2one('res.users', string='Match Maker (Sales)', default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('mm.lead.seq') or 'New Match'
        return super(MatchMakingLead, self).create(vals_list)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        """Chữ ký chuẩn xác nhận đủ 3 tham số truyền vào từ ORM Odoo 19"""
        return ['new', 'qualified', 'proposition', 'won', 'lost']
