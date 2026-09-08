from odoo import models, fields

class LeadCategory(models.Model):
    _name = 'lead.category'
    _description = 'Loại nhu cầu / Lĩnh vực Lead'
    
    name = fields.Char(string="Tên loại", required=True)
    code = fields.Char(string="Mã loại", required=True, unique=True)
    description = fields.Text(string="Mô tả")
    icon = fields.Char(string="Icon", help="Font Awesome icon class")
    color = fields.Char(string="Màu sắc", help="Hex color code")
    sequence = fields.Integer(string="Thứ tự", default=10)
    active = fields.Boolean(default=True)
    
    lead_ids = fields.One2many('crm.lead', 'lead_category', string="Leads")
    lead_count = fields.Integer(
        string="Số Lead",
        compute='_compute_lead_count'
    )
    
    def _compute_lead_count(self):
        for category in self:
            category.lead_count = len(category.lead_ids.filtered(
                lambda l: l.approval_status == 'approved'
            ))
