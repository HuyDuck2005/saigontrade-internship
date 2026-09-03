from odoo import models, fields, api

class TaskPresentation(models.Model):
    _name = 'task.presentation'
    _description = 'Lịch Thuyết Trình'

    name = fields.Char(string='Chủ đề thuyết trình', required=True)
    presenter_id = fields.Many2one('hr.employee', string='Người trình bày', required=True, default=lambda self: self.env.user.employee_id)
    presentation_date = fields.Datetime(string='Thời gian dự kiến', required=True)
    
    task_ids = fields.Many2many('project.task', string='Tasks Báo Cáo')
    reviewer_ids = fields.Many2many('hr.employee', 'presentation_reviewer_rel', string='Người tham gia')
    
    # CẦU NỐI KÉO DỮ LIỆU ĐÁNH GIÁ VÀO
    feedback_ids = fields.One2many('work.feedback', 'presentation_id', string='Nhận xét & Chấm điểm')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('scheduled', 'Đã Lên Lịch'),
        ('completed', 'Đã Hoàn Thành')
    ], string='Trạng thái', default='draft')

    def action_schedule(self):
        for record in self:
            record.state = 'scheduled'

    def action_complete(self):
        for record in self:
            record.state = 'completed'
