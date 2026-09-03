from odoo import models, api

class Project(models.Model):
    _inherit = 'project.project'

    @api.model_create_multi
    def create(self, vals_list):
        # 1. Để Odoo tạo Dự án như bình thường
        projects = super(Project, self).create(vals_list)
        
        # 2. Ngay sau khi tạo xong, ép hệ thống đẻ ra 3 cột
        for project in projects:
            stages = ['Cần làm (To Do)', 'Đang làm (In Progress)', 'Đã xong (Done)']
            for seq, name in enumerate(stages):
                self.env['project.task.type'].create({
                    'name': name,
                    'sequence': seq,
                    'project_ids': [(4, project.id)]
                })
        return projects
