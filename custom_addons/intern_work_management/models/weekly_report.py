from odoo import models, fields, api

class WeeklyReport(models.Model):
    _name = 'weekly.report'
    _description = 'Báo cáo tuần'

    name = fields.Char(string='Tiêu đề', required=True, copy=False, default='Draft')
    employee_id = fields.Many2one('hr.employee', string='Người báo cáo', required=True, default=lambda self: self.env.user.employee_id)
    start_date = fields.Date(string='Ngày bắt đầu tuần', required=True)
    end_date = fields.Date(string='Ngày kết thúc tuần', required=True)
    
    completed_task_ids = fields.Many2many('project.task', 'weekly_completed_task_rel', string='Task đã hoàn thành')
    in_progress_task_ids = fields.Many2many('project.task', 'weekly_progress_task_rel', string='Task đang thực hiện')
    issues_summary = fields.Text(string='Tổng hợp Vấn đề & Bài học')
    next_week_plan = fields.Text(string='Kế hoạch tuần tới')
    
    manager_score = fields.Selection([('1','1 Sao'),('2','2 Sao'),('3','3 Sao'),('4','4 Sao'),('5','5 Sao')], string='Điểm đánh giá')
    manager_feedback = fields.Text(string='Nhận xét của Quản lý')
    
    state = fields.Selection([('draft', 'Nháp'), ('submitted', 'Đã nộp'), ('reviewed', 'Đã Review')], string='Trạng thái', default='draft')

    def action_submit(self):
        for record in self:
            record.state = 'submitted'

    def action_review(self):
        for record in self:
            record.state = 'reviewed'
