from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class CreateDealWizard(models.TransientModel):
    _name = 'create.deal.wizard'
    _description = 'Wizard Tạo Deal từ Danh sách Contact - Advanced'

    partner_ids = fields.Many2many('res.partner', string='Danh sách Contact đã chọn', required=True)
    deal_name = fields.Char(string='Tên Deal / Tiêu đề cơ hội', required=True, default='Cơ hội Hợp tác 2026')
    expected_revenue = fields.Monetary(string='Doanh thu dự kiến (Amount)', default=0.0)
    company_currency = fields.Many2one(string='Tiền tệ', related='create_uid.company_id.currency_id', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    event = fields.Char(string='Sự kiện (Event)', default='SGT TechFest 2026')
    event_location = fields.Char(string='Địa điểm sự kiện', default='TP. Hồ Chí Minh')
    notes = fields.Text(string='Ghi chú nội dung')
    
    # Cải tiến nghiệp vụ: Tùy chọn xử lý khi trùng lặp hoặc khác chủ sở hữu
    duplicate_action = fields.Selection([
        ('allow', 'Vẫn tạo Deal mới bình thường (Khuyên dùng)'),
        ('skip', 'Bỏ qua nếu khách hàng đã có Deal trong sự kiện này')
    ], string='Xử lý khi trùng sự kiện', default='allow', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(CreateDealWizard, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids and self.env.context.get('active_model') == 'res.partner':
            res['partner_ids'] = [(6, 0, active_ids)]
        return res

    def action_create_deals(self):
        self.ensure_one()
        if not self.partner_ids:
            raise UserError('Vui lòng chọn ít nhất một Contact để tạo Deal!')

        created_lead_ids = []
        skipped_count = 0
        ownership_warnings = 0

        current_user = self.env.user

        for partner in self.partner_ids:
            # 1. KIỂM TRA LỖI 1: Trùng lặp sự kiện
            if self.event:
                existing_deal = self.env['crm.lead'].search([
                    ('partner_id', '=', partner.id),
                    ('description', 'like', f"Event: {self.event}")
                ], limit=1)
                
                if existing_deal and self.duplicate_action == 'skip':
                    skipped_count += 1
                    continue # Bỏ qua nếu user chọn chế độ skip

            # 2. KIỂM TRA LỖI 2: Xung đột Phân công Salesperson (Deal Ownership)
            # Nếu partner đã có người phụ trách khác người đang bấm nút tạo
            assigned_salesperson = partner.user_id
            deal_user_id = current_user.id
            
            if assigned_salesperson and assigned_salesperson.id != current_user.id:
                ownership_warnings += 1
                # Nghiệp vụ chuẩn: Giữ nguyên người phụ trách cũ cho khách hàng để tránh tranh chấp
                deal_user_id = assigned_salesperson.id

            lead_name = f"{self.deal_name} - {partner.name}"
            lead_vals = {
                'name': lead_name,
                'partner_id': partner.id,
                'user_id': deal_user_id, # Giữ đúng chủ sở hữu cũ nếu có
                'contact_name': partner.name,
                'phone': partner.phone or partner.mobile or '',
                'email_from': partner.email or '',
                'expected_revenue': self.expected_revenue,
                'description': f"Event: {self.event or 'N/A'} | Location: {self.event_location or 'N/A'}\nNotes: {self.notes or ''}".strip(),
            }

            lead = self.env['crm.lead'].create(lead_vals)
            created_lead_ids.append(lead.id)

        _logger.info(f"Wizard tạo deal hoàn tất. Tạo mới: {len(created_lead_ids)}, Bỏ qua: {skipped_count}, Cảnh báo phân công: {ownership_warnings}")

        return {
            'name': 'Danh sách Deal vừa tạo',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'tree,form',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [('id', 'in', created_lead_ids)],
            'target': 'current',
        }
