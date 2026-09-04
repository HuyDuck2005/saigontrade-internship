from odoo import models, fields, api
from odoo.exceptions import UserError

class Project(models.Model):
    _inherit = 'project.project'

    # LiÃªn káº¿t dá»± Ã¡n vá»›i TTS
    intern_id = fields.Many2one('hr.employee', string='Thá»±c táº­p sinh chá»§ quáº£n')
    
    # CÃ¡c trÆ°á»ng tÃ­nh toÃ¡n cho giao diá»‡n Cáº£nh bÃ¡o ngoÃ i báº£ng
    report_count = fields.Integer(compute='_compute_report_stats', string='Tá»•ng bÃ¡o cÃ¡o')
    pending_report_count = fields.Integer(compute='_compute_report_stats', string='Chá» duyá»‡t')
    last_report_date = fields.Date(compute='_compute_report_stats', string='BÃ¡o cÃ¡o gáº§n nháº¥t')

    def _compute_report_stats(self):
        for project in self:
            if project.intern_id:
                reports = self.env['daily.report'].search([('employee_id', '=', project.intern_id.id)])
                project.report_count = len(reports)
                project.pending_report_count = len(reports.filtered(lambda r: r.state == 'submitted'))
                project.last_report_date = max(reports.mapped('report_date')) if reports else False
            else:
                project.report_count = 0
                project.pending_report_count = 0
                project.last_report_date = False

    def action_open_intern_reports(self):
        self.ensure_one()
        return {
            'name': f'BÃ¡o cÃ¡o cá»§a {self.intern_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'daily.report',
            'domain': [('employee_id', '=', self.intern_id.id)],
            'view_mode': 'tree,form',
            'context': {'default_employee_id': self.intern_id.id}
        }

    @api.model_create_multi
    def create(self, vals_list):
        projects = super(Project, self).create(vals_list)
        for project in projects:
            stages = ['Cáº§n lÃ m (To Do)', 'Äang lÃ m (In Progress)', 'ÄÃ£ xong (Done)']
            for seq, name in enumerate(stages):
                self.env['project.task.type'].create({
                    'name': name,
                    'sequence': seq,
                    'project_ids': [(4, project.id)]
                })
        return projects

class ProjectTask(models.Model):
    _inherit = 'project.task'

    campaign_id = fields.Many2one('intern.assessment.campaign', string='Chiến dịch Đánh giá')

    def action_split_subtasks(self):
        for task in self:
            if not task.user_ids or len(task.user_ids) <= 1:
                raise UserError("Task nÃ y cáº§n cÃ³ tá»« 2 ngÆ°á»i phá»¥ trÃ¡ch trá»Ÿ lÃªn Ä‘á»ƒ cÃ³ thá»ƒ chia nhá»!")
            for user in task.user_ids:
                self.env['project.task'].create({
                    'name': f"{task.name} ({user.name})",
                    'project_id': task.project_id.id,
                    'parent_id': task.id,
                    'user_ids': [(6, 0, [user.id])]
                })
            task.user_ids = [(5, 0, 0)]
