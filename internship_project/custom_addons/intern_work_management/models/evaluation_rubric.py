from odoo import models, fields, api, _

class EvaluationRubric(models.Model):
    _name = 'evaluation.rubric'
    _description = 'Evaluation Rubric'

    name = fields.Char("Tên Bảng Tiêu Chí", required=True)
    description = fields.Text("Mô tả")
    criteria_ids = fields.One2many('evaluation.criteria', 'rubric_id', string="Danh sách tiêu chí")

class EvaluationCriteria(models.Model):
    _name = 'evaluation.criteria'
    _description = 'Evaluation Criteria'

    name = fields.Char("Tên Tiêu Chí", required=True)
    rubric_id = fields.Many2one('evaluation.rubric', string="Bảng Tiêu Chí", required=True, ondelete='cascade')
    weight = fields.Float("Trọng số (%)", required=True, default=10.0)
    description = fields.Text("Hướng dẫn đánh giá")