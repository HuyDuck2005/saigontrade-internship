from odoo import models, fields

class LeadGalleryImage(models.Model):
    _name = 'lead.gallery.image'
    _description = 'Thư viện ảnh chi tiết Lead'
    
    lead_id = fields.Many2one('crm.lead', string='Lead', ondelete='cascade')
    image = fields.Image('Hình ảnh', required=True, max_width=1200, max_height=1200)
    name = fields.Char('Miêu tả / Tên sản phẩm', default='Ảnh sản phẩm')
    mimetype = fields.Char('Mimetype', default='image/jpeg')

class CrmLeadGallery(models.Model):
    _inherit = 'crm.lead'
    
    gallery_image_ids = fields.One2many('lead.gallery.image', 'lead_id', string='Thư viện ảnh Sản phẩm / Nhà sản xuất')
