from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WeeklyReport(models.Model):
    _name = 'weekly.report'
    _description = 'Báo cáo tuần'

    name = fields.Char(string='Tiêu đề', required=True, copy=False, default='Draft')
    employee_id = fields.Many2one(
        'hr.employee', 
        string='Người báo cáo', 
        required=True, 
        default=lambda self: self.env.user.employee_id.id if self.env.user.employee_id else False
    )
    start_date = fields.Date(string='Ngày bắt đầu tuần', required=True)
    end_date = fields.Date(string='Ngày kết thúc tuần', required=True)
    
    completed_task_ids = fields.Many2many(
        'project.task', 'weekly_completed_task_rel', 
        string='Task đã hoàn thành', 
        compute='_compute_tasks_from_daily', store=True, readonly=True
    )
    in_progress_task_ids = fields.Many2many(
        'project.task', 'weekly_progress_task_rel', 
        string='Task đang thực hiện', 
        compute='_compute_tasks_from_daily', store=True, readonly=True
    )
    
    issues_summary = fields.Text(string='Tổng hợp Vấn đề & Bài học')
    next_week_plan = fields.Text(string='Kế hoạch tuần tới')
    
    manager_score = fields.Selection([('1','1 Sao'),('2','2 Sao'),('3','3 Sao'),('4','4 Sao'),('5','5 Sao')], string='Điểm đánh giá')
    manager_feedback = fields.Text(string='Nhận xét của Quản lý')
    
    state = fields.Selection([('draft', 'Nháp'), ('submitted', 'Đã nộp'), ('reviewed', 'Đã Review')], string='Trạng thái', default='draft')

    @api.constrains('employee_id')
    def _check_employee(self):
        for record in self:
            if not record.employee_id:
                raise ValidationError("Tài khoản của bạn chưa được liên kết với Hồ sơ nhân viên. Vui lòng liên hệ Admin!")

    @api.depends('employee_id', 'start_date', 'end_date')
    def _compute_tasks_from_daily(self):
        for record in self:
            if record.employee_id and record.start_date and record.end_date:
                daily_reports = self.env['daily.report'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('report_date', '>=', record.start_date),
                    ('report_date', '<=', record.end_date),
                    ('state', 'in', ['submitted', 'reviewed'])
                ])
                record.completed_task_ids = [(6, 0, daily_reports.mapped('completed_task_ids').ids)]
                record.in_progress_task_ids = [(6, 0, daily_reports.mapped('in_progress_task_ids').ids)]
            else:
                record.completed_task_ids = [(5, 0, 0)]
                record.in_progress_task_ids = [(5, 0, 0)]

    def action_submit(self):
        for record in self:
            record.state = 'submitted'

    def action_review(self):
        for record in self:
            record.state = 'reviewed'
