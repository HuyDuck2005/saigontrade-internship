import base64
import csv
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class InternAssessmentCampaign(models.Model):
    _name = 'intern.assessment.campaign'
    _description = 'Evaluation Campaign for Multiple Interns'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Tên Chiến Dịch", required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string="Phòng Ban", tracking=True)
    intern_ids = fields.Many2many(
        'hr.employee', 
        'campaign_intern_rel', 
        'campaign_id', 
        'employee_id', 
        string="Danh sách Thực tập sinh",
        domain=[('employee_type', '=', 'intern')]
    )
    
    task_template_file = fields.Binary("Tải lên File CSV mẫu Task")
    task_template_filename = fields.Char("Tên file")
    task_ids = fields.One2many('project.task', 'campaign_id', string="Danh sách Task được tạo")
    
    evaluation_rubric_id = fields.Many2one('evaluation.rubric', string="Bảng Tiêu Chí Đánh Giá", tracking=True)
    
    start_date = fields.Date("Ngày bắt đầu", tracking=True)
    end_date = fields.Date("Ngày kết thúc", tracking=True)
    status = fields.Selection([
        ('draft', 'Nháp'),
        ('assigned', 'Đã Giao Task'),
        ('in_progress', 'Đang Thực Hiện'),
        ('completed', 'Đã Hoàn Thành')
    ], string="Trạng thái", default='draft', tracking=True)

    def action_import_and_assign_tasks(self):
        self.ensure_one()
        if not self.task_template_file:
            raise UserError(_("Vui lòng tải lên File CSV chứa Task mẫu!"))
        if not self.intern_ids:
            raise UserError(_("Vui lòng chọn ít nhất 1 Thực tập sinh để giao Task!"))

        try:
            csv_data = base64.b64decode(self.task_template_file).decode('utf-8-sig')
            reader = csv.DictReader(StringIO(csv_data))
        except Exception as e:
            raise UserError(_("Lỗi khi đọc file CSV! Đảm bảo định dạng chuẩn UTF-8. Chi tiết: %s") % str(e))

        if not reader.fieldnames or 'task_name' not in reader.fieldnames:
            raise UserError(_("File CSV thiếu cột bắt buộc: 'task_name' (Tên Task)."))

        new_tasks = []
        for row in reader:
            task_name = row.get('task_name', 'No Name Task')
            deadline = row.get('deadline', False)
            description = row.get('description', '')
            
            for intern in self.intern_ids:
                if not intern.user_id:
                    continue
                    
                project = self.env['project.project'].search([('intern_id', '=', intern.id)], limit=1)
                
                vals = {
                    'name': f"[{self.name}] {task_name}",
                    'description': description,
                    'campaign_id': self.id,
                    'user_ids': [(6, 0, [intern.user_id.id])],
                }
                
                if project:
                    vals['project_id'] = project.id
                    
                if deadline:
                    vals['date_deadline'] = deadline

                new_tasks.append(vals)

        if new_tasks:
            self.env['project.task'].create(new_tasks)
            self.status = 'assigned'
            self.message_post(body=_("Đã import và giao thành công %s task cho %s thực tập sinh.") % (len(new_tasks), len(self.intern_ids)))
        else:
            raise UserError(_("Không có Task nào được tạo. Vui lòng kiểm tra lại file dữ liệu hoặc danh sách Intern."))

    def action_start_campaign(self):
        self.status = 'in_progress'

    def action_complete_campaign(self):
        self.status = 'completed'

class InternAssessmentDashboard(models.Model):
    _name = 'intern.assessment.dashboard'
    _description = 'Leader View - Performance Overview (Abstract)'
    _auto = False 