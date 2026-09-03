from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class DailyReport(models.Model):
    _name = 'daily.report'
    _description = 'Báo cáo hằng ngày'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tiêu đề', required=True, copy=False, default='Draft', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Người báo cáo', required=True, default=lambda self: self.env.user.employee_id, tracking=True)
    report_date = fields.Date(string='Ngày báo cáo', required=True, default=fields.Date.context_today, tracking=True)
    need_support = fields.Boolean(string='Cần hỗ trợ gấp', tracking=True)
    
    completed_task_ids = fields.Many2many('project.task', 'daily_completed_task_rel', string='Task đã hoàn thành')
    in_progress_task_ids = fields.Many2many('project.task', 'daily_progress_task_rel', string='Task đang thực hiện')
    
    problem_description = fields.Text(string='Vấn đề gặp phải', tracking=True)
    solution_description = fields.Text(string='Cách giải quyết', tracking=True)
    next_day_plan = fields.Text(string='Kế hoạch ngày mai', tracking=True)
    
    attachment_ids = fields.Many2many('ir.attachment', string='Tài liệu/Ảnh minh chứng')
    support_response = fields.Text(string='Hướng dẫn/Hỗ trợ từ Admin', tracking=True)
    manager_score = fields.Selection([('1','1 Sao'),('2','2 Sao'),('3','3 Sao'),('4','4 Sao'),('5','5 Sao')], string='Điểm đánh giá', tracking=True)
    manager_feedback = fields.Text(string='Nhận xét của Quản lý', tracking=True)

    state = fields.Selection([('draft', 'Nháp'), ('submitted', 'Đã nộp'), ('reviewed', 'Đã Review')], string='Trạng thái', default='draft', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("Hệ thống nghiêm cấm xóa vĩnh viễn báo cáo đã nộp! Vui lòng dùng tính năng Lưu Trữ.")
        return super(DailyReport, self).unlink()

    def action_submit(self):
        for record in self:
            record.state = 'submitted'

    def action_review(self):
        for record in self:
            if not record.manager_score:
                raise ValidationError("Quản lý vui lòng chọn Điểm đánh giá (Số Sao) trước khi Chốt Review!")
            record.state = 'reviewed'
            if record.create_uid:
                record.message_post(
                    body=f"🎉 <b>BÁO CÁO ĐÃ ĐƯỢC CHỐT!</b><br/>Admin đã chấm <b>{record.manager_score} Sao</b> cho bạn.",
                    partner_ids=[record.create_uid.partner_id.id],
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )

    def action_resolve_support(self):
        for record in self:
            record.need_support = False

    def action_request_revision(self):
        for record in self:
            record.state = 'draft'
            if record.create_uid:
                record.message_post(
                    body="⚠️ <b>YÊU CẦU SỬA LẠI:</b> Admin đã trả lại báo cáo này. Vui lòng nộp lại nhé!",
                    partner_ids=[record.create_uid.partner_id.id],
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )

    def action_unlock_admin(self):
        for record in self:
            record.state = 'submitted'

    def action_open_form_view(self):
        self.ensure_one()
        return {
            'name': 'Chi tiết Báo cáo',
            'type': 'ir.actions.act_window',
            'res_model': 'daily.report',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_full_screen(self):
        self.ensure_one()
        return {
            'name': 'Chi tiết Báo cáo',
            'type': 'ir.actions.act_window',
            'res_model': 'daily.report',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'main',
        }

    # ========================================================
    # HÀM MỚI: ROBOT TỰ ĐỘNG NHẮC NHỞ (CRON JOB)
    # ========================================================
    @api.model
    def cron_remind_daily_report(self):
        today = fields.Date.context_today(self)
        admin_group = self.env.ref('base.group_erp_manager')
        
        # Lấy danh sách tất cả nhân viên có tài khoản đăng nhập
        employees = self.env['hr.employee'].search([('user_id', '!=', False)])
        
        for emp in employees:
            # Bỏ qua Admin (Admin không cần nộp báo cáo)
            if admin_group in emp.user_id.groups_id:
                continue
                
            # Tìm xem hôm nay nhân viên này có báo cáo nào 'Đã nộp' hoặc 'Đã Review' chưa?
            report = self.search([
                ('employee_id', '=', emp.id), 
                ('report_date', '=', today), 
                ('state', 'in', ['submitted', 'reviewed'])
            ], limit=1)
            
            # Nếu KHÔNG tìm thấy báo cáo đã nộp -> Nhắn tin nhắc nhở!
            if not report:
                emp.user_id.partner_id.message_post(
                    body="⏰ <b>TÍT TÍT! NHẮC NHỞ TỰ ĐỘNG:</b><br/>Đã 17h00 rồi! Đừng quên nộp Báo cáo ngày hôm nay trên hệ thống nhé bạn ơi!",
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=self.env.ref('base.partner_root').id  # Tin nhắn gửi từ System/OdooBot
                )
