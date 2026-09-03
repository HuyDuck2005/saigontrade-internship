from odoo import models, fields, api
from datetime import timedelta
import calendar

class InternDashboard(models.Model):
    _name = 'intern.dashboard'
    _description = 'Bảng Thống Kê Tổng Quan'

    name = fields.Char(default='Bảng Điều Khiển (KPI)')

    total_reports = fields.Integer(compute='_compute_kpi')
    total_tasks_done = fields.Integer(compute='_compute_kpi')
    total_tasks_progress = fields.Integer(compute='_compute_kpi')
    urgent_report_ids = fields.Many2many('daily.report', 'dash_urgent_rel', compute='_compute_urgent', string='Cần hỗ trợ gấp')

    filter_date = fields.Date(string='Mốc thời gian', default=fields.Date.context_today)
    filter_type = fields.Selection([('day', 'Theo Ngày'), ('week', 'Theo Tuần'), ('month', 'Theo Tháng')], string='Kiểu lọc', default='day')
    filtered_report_ids = fields.Many2many('daily.report', 'dash_filtered_rel', compute='_compute_filtered_reports')

    def _compute_kpi(self):
        for rec in self:
            # LỌC BỎ BẢN NHÁP: Admin chỉ thấy những gì đã nộp
            reports = self.env['daily.report'].search([('state', '!=', 'draft')])
            rec.total_reports = len(reports)
            rec.total_tasks_done = len(reports.mapped('completed_task_ids'))
            rec.total_tasks_progress = len(reports.mapped('in_progress_task_ids'))

    def _compute_urgent(self):
        for rec in self:
            rec.urgent_report_ids = self.env['daily.report'].search([('need_support', '=', True), ('state', '!=', 'draft')]).ids

    @api.depends('filter_date', 'filter_type')
    def _compute_filtered_reports(self):
        for rec in self:
            if not rec.filter_date:
                rec.filter_date = fields.Date.context_today(self)
            
            # ẨN BẢN NHÁP TRÊN DANH SÁCH BÁO CÁO CỦA DASHBOARD
            domain = [('state', '!=', 'draft')]
            
            if rec.filter_type == 'day':
                domain.append(('report_date', '=', rec.filter_date))
            elif rec.filter_type == 'week':
                start = rec.filter_date - timedelta(days=rec.filter_date.weekday())
                end = start + timedelta(days=6)
                domain.extend([('report_date', '>=', start), ('report_date', '<=', end)])
            elif rec.filter_type == 'month':
                start = rec.filter_date.replace(day=1)
                last_day = calendar.monthrange(start.year, start.month)[1]
                end = rec.filter_date.replace(day=last_day)
                domain.extend([('report_date', '>=', start), ('report_date', '<=', end)])
            
            rec.filtered_report_ids = self.env['daily.report'].search(domain, order='report_date desc').ids

    def action_open_reports(self):
        return {
            'name': 'Tất cả Báo Cáo',
            'type': 'ir.actions.act_window',
            'res_model': 'daily.report',
            # CHẶN XEM NHÁP KHI BẤM VÀO NÚT TỔNG BÁO CÁO
            'domain': [('state', '!=', 'draft')],
            'view_mode': 'tree,form,graph,pivot',
        }

    def action_open_done_tasks(self):
        task_ids = self.env['daily.report'].search([('state', '!=', 'draft')]).mapped('completed_task_ids').ids
        return {
            'name': 'Tasks Đã Hoàn Thành',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'domain': [('id', 'in', task_ids)],
            'view_mode': 'tree,form',
        }

    def action_open_progress_tasks(self):
        task_ids = self.env['daily.report'].search([('state', '!=', 'draft')]).mapped('in_progress_task_ids').ids
        return {
            'name': 'Tasks Đang Thực Hiện',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'domain': [('id', 'in', task_ids)],
            'view_mode': 'tree,form',
        }
