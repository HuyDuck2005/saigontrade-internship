from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    # ===== TRƯỜNG BỔ SUNG NÂNG CAO =====
    referred_lead_id = fields.Many2one('crm.lead', string="Lead nguồn từ Website", readonly=True)
    is_verified = fields.Boolean(string="Doanh nghiệp Đã Xác Minh", default=False, help="Hiển thị tích xanh xác thực uy tín trên sàn")
    expiration_date = fields.Date(string="Ngày hết hạn hiển thị", help="Sau ngày này lead sẽ tự động ẩn khỏi website")
    brochure_file = fields.Binary(string="Catalogue / Hồ sơ năng lực (PDF)", attachment=True)
    brochure_filename = fields.Char(string="Tên tệp Catalogue")

    # ===== FIELDS HIỂN THỊ WEBSITE =====
    website_visible = fields.Boolean(
        string="Hiển thị trên Website",
        default=False,
        help="Có hiển thị lead này trên website công khai hay không"
    )
    
    approval_status = fields.Selection([
        ('draft', 'Chưa duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ], string="Trạng thái duyệt", default='draft')
    
    approval_date = fields.Datetime(
        string="Ngày duyệt",
        readonly=True
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string="Người duyệt",
        readonly=True
    )
    
    rejection_reason = fields.Text(
        string="Lý do từ chối"
    )
    
    lead_image = fields.Image(
        string="Hình ảnh Lead",
        help="Ảnh đại diện cho lead trên website"
    )
    
    lead_intent = fields.Selection([
        ('buy', 'TÌM MUA'),
        ('sell', 'CHÀO BÁN'),
        ('partner', 'TÌM ĐỐI TÁC')
    ], string="Phân loại nhu cầu", default='buy')
    
    lead_category = fields.Many2one(
        'lead.category',
        string="Loại nhu cầu/Lĩnh vực"
    )
    
    country_region = fields.Char(
        string="Quốc gia/Khu vực"
    )
    
    short_description = fields.Text(
        string="Mô tả ngắn"
    )
    
    website_published_date = fields.Datetime(
        string="Ngày xuất bản",
        readonly=True
    )
    
    contact_person = fields.Char(string="Người liên hệ")
    contact_phone = fields.Char(string="Số điện thoại")
    contact_email = fields.Char(string="Email")
    
    website_view_count = fields.Integer(string="Lượt xem", default=0, readonly=True)
    website_contact_count = fields.Integer(string="Lượt liên hệ", default=0, readonly=True)
    
    last_approval_action = fields.Selection([
        ('submitted', 'Vừa được submit'),
        ('reviewed', 'Đã được review'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Bị từ chối'),
        ('resubmitted', 'Được resubmit sau từ chối'),
    ], string="Hành động duyệt cuối cùng", readonly=True)
    
    approval_history = fields.One2many(
        'lead.approval.history',
        'lead_id',
        string="Lịch sử duyệt",
        readonly=True
    )
    
    @api.model
    def create(self, vals):
        record = super().create(vals)
        self.env['lead.approval.history'].create({
            'lead_id': record.id,
            'action': 'submitted',
            'performed_by': self.env.user.id,
            'notes': f"Cơ hội được khởi tạo bởi {self.env.user.name}",
        })
        record._send_approval_notification(record)
        return record
    
    def action_approve(self):
        if not self.env.user.has_group('website_lead_showcase.group_lead_approver'):
            raise ValidationError("Bạn không có quyền phê duyệt Lead")
        
        if self.approval_status == 'approved':
            raise ValidationError("Lead này đã được phê duyệt rồi")
        
        self.write({
            'approval_status': 'approved',
            'website_visible': True,
            'website_published_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })
        
        self.env['lead.approval.history'].create({
            'lead_id': self.id,
            'action': 'approved',
            'performed_by': self.env.user.id,
            'notes': 'Đã duyệt và xuất bản lên Website SaiGonTrade',
        })
        self._send_approval_confirmation_email()
    
    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lead.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }
    
    def action_resubmit(self):
        if self.approval_status != 'rejected':
            raise ValidationError("Chỉ có thể gửi lại Lead bị từ chối")
        
        self.write({
            'approval_status': 'draft',
            'rejection_reason': '',
        })
        
        self.env['lead.approval.history'].create({
            'lead_id': self.id,
            'action': 'resubmitted',
            'performed_by': self.env.user.id,
        })
        self._send_approval_notification(self)
    
    def _send_approval_notification(self, record):
        template = self.env.ref('website_lead_showcase.email_lead_approval_request', raise_if_not_found=False)
        if template:
            approvers = self.env['res.users'].search([
                ('group_ids', 'in', self.env.ref('website_lead_showcase.group_lead_approver').id)
            ])
            for approver in approvers:
                template.send_mail(record.id, force_send=False)
    
    def _send_approval_confirmation_email(self):
        template = self.env.ref('website_lead_showcase.email_lead_approved', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=False)
