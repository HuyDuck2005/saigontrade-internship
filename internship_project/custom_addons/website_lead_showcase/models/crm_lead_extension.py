from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    # ===== TRƯỜNG BỔ SUNG =====
    referred_lead_id = fields.Many2one('crm.lead', string="Lead nguồn từ Website", readonly=True, help="Khách hàng liên hệ từ Lead này")
    
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
        readonly=True,
        help="Thời gian Admin phê duyệt lead"
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string="Người duyệt",
        readonly=True
    )
    
    rejection_reason = fields.Text(
        string="Lý do từ chối",
        help="Lý do nếu admin từ chối duyệt lead"
    )
    
    # ===== FIELDS HIỂN THỊ TRÊN CARD =====
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
        string="Loại nhu cầu/Lĩnh vực",
        help="Phân loại nhu cầu của lead"
    )
    
    country_region = fields.Char(
        string="Quốc gia/Khu vực",
        help="Nơi lead đó cần hỗ trợ"
    )
    
    short_description = fields.Text(
        string="Mô tả ngắn",
        help="Mô tả tóm tắt về lead (hiển thị trên card)"
    )
    
    website_published_date = fields.Datetime(
        string="Ngày xuất bản",
        readonly=True,
        help="Thời gian lead được xuất bản trên website"
    )
    
    contact_person = fields.Char(
        string="Người liên hệ",
        help="Tên người liên hệ"
    )
    
    contact_phone = fields.Char(
        string="Số điện thoại liên hệ",
        help="Điện thoại để liên hệ"
    )
    
    contact_email = fields.Char(
        string="Email liên hệ",
        help="Email để liên hệ"
    )
    
    # ===== FIELDS THỐNG KÊ =====
    website_view_count = fields.Integer(
        string="Lượt xem trên website",
        default=0,
        readonly=True
    )
    
    website_contact_count = fields.Integer(
        string="Số lần được liên hệ từ website",
        default=0,
        readonly=True
    )
    
    # ===== WORKFLOW FIELDS =====
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
        """Override create để tự động ghi approval history"""
        record = super().create(vals)
        
        # Tạo approval history record
        self.env['lead.approval.history'].create({
            'lead_id': record.id,
            'action': 'submitted',
            'performed_by': self.env.user.id,
            'notes': f"Lead được tạo bởi {self.env.user.name}",
        })
        
        # Gửi email thông báo đến approvers
        record._send_approval_notification(record)
        
        return record
    
    def action_approve(self):
        """Phê duyệt Lead"""
        # Check permission
        if not self.env.user.has_group('website_lead_showcase.group_lead_approver'):
            raise ValidationError("Bạn không có quyền phê duyệt Lead")
        
        # Check business rules
        if self.approval_status == 'approved':
            raise ValidationError("Lead này đã được phê duyệt rồi")
        
        if not self.lead_image:
            raise ValidationError("Lead phải có hình ảnh trước khi phê duyệt")
        
        if not self.short_description:
            raise ValidationError("Lead phải có mô tả trước khi phê duyệt")
        
        # Update lead
        self.write({
            'approval_status': 'approved',
            'website_visible': True,
            'website_published_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })
        
        # Record history
        self.env['lead.approval.history'].create({
            'lead_id': self.id,
            'action': 'approved',
            'performed_by': self.env.user.id,
            'notes': 'Lead được phê duyệt và xuất bản trên website',
        })
        
        # Send confirmation email
        self._send_approval_confirmation_email()
    
    def action_reject(self):
        """Từ chối Lead"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lead.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }
    
    def action_resubmit(self):
        """Gửi lại Lead"""
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
        """Gửi email thông báo đến approvers"""
        template = self.env.ref(
            'website_lead_showcase.email_lead_approval_request', raise_if_not_found=False
        )
        if template:
            approvers = self.env['res.users'].search([
                ('group_ids', 'in', 
                 self.env.ref('website_lead_showcase.group_lead_approver').id)
            ])
            for approver in approvers:
                template.send_mail(record.id, force_send=False)
    
    def _send_approval_confirmation_email(self):
        """Gửi email xác nhận phê duyệt"""
        template = self.env.ref(
            'website_lead_showcase.email_lead_approved', raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=False)
    
    @api.constrains('lead_image', 'short_description')
    def _check_required_fields_for_approval(self):
        """Kiểm tra fields bắt buộc khi phê duyệt"""
        for record in self:
            if record.approval_status == 'approved':
                if not record.lead_image:
                    raise ValidationError(
                        f"Lead '{record.name}' phải có hình ảnh"
                    )
                if not record.short_description:
                    raise ValidationError(
                        f"Lead '{record.name}' phải có mô tả"
                    )
