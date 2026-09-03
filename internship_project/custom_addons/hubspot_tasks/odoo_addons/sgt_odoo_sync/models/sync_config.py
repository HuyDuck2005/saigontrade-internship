from odoo import models, fields, api

class SyncConfiguration(models.Model):
    _name = 'sync.configuration'
    _description = 'Cấu hình ánh xạ trường dữ liệu động (Dynamic Sync Mapping)'

    name = fields.Char(string='Tên quy tắc', required=True, 
                       help="Ví dụ: Ánh xạ Chức vụ sang Odoo 2")
    
    model_id = fields.Many2one('ir.model', string='Đối tượng nguồn (Model)', 
                               required=True, ondelete='cascade')
    
    field_id = fields.Many2one('ir.model.fields', string='Trường Odoo 1 (Local Field)', 
                               required=True, ondelete='cascade',
                               domain="[('model_id', '=', model_id)]")
    
    remote_field_name = fields.Char(string='Trường Odoo 2 (Remote Field)', required=True, 
                                     help="Tên biến bên API/Odoo 2 (VD: x_custome_fields_jobtitle)")
    
    active = fields.Boolean(string='Kích hoạt', default=True)

    security_group_ids = fields.Many2many('res.groups', string='Nhóm quyền (Security Groups)', 
                                          help="Để trống nếu áp dụng cho mọi User. Nếu chọn, chỉ user thuộc nhóm này mới đẩy dữ liệu đi.")

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            self.field_id = False
