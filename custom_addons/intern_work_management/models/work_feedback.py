from odoo import models, fields, api

class WorkFeedback(models.Model):
    _name = 'work.feedback'
    _description = 'Đánh giá / Feedback'
    _rec_name = 'presentation_id'
    
    presentation_id = fields.Many2one('task.presentation', string='Buổi thuyết trình', required=True)
    reviewer_id = fields.Many2one('hr.employee', string='Người đánh giá', default=lambda self: self.env.user.employee_id)
    employee_id = fields.Many2one('hr.employee', related='presentation_id.presenter_id', string='Người nhận đánh giá', store=True)
    
    # Tiêu chí đánh giá (Chấm điểm 1-5 sao)
    score_technical = fields.Selection([(str(i), str(i)) for i in range(1, 6)], string='Kỹ thuật (1-5)')
    score_understanding = fields.Selection([(str(i), str(i)) for i in range(1, 6)], string='Mức độ hiểu (1-5)')
    score_problem_solving = fields.Selection([(str(i), str(i)) for i in range(1, 6)], string='Giải quyết vấn đề (1-5)')
    score_communication = fields.Selection([(str(i), str(i)) for i in range(1, 6)], string='Kỹ năng trình bày (1-5)')
    
    overall_score = fields.Float(string='Điểm tổng quát (Thang 10)', compute='_compute_overall_score', store=True)
    comments = fields.Text(string='Nhận xét chi tiết')

    @api.depends('score_technical', 'score_understanding', 'score_problem_solving', 'score_communication')
    def _compute_overall_score(self):
        for record in self:
            scores = [
                int(record.score_technical or 0),
                int(record.score_understanding or 0),
                int(record.score_problem_solving or 0),
                int(record.score_communication or 0)
            ]
            total = sum(scores)
            # 4 tiêu chí, điểm tối đa là 20. Quy đổi ra thang điểm 10.
            record.overall_score = (total / 20.0) * 10 if total > 0 else 0.0
