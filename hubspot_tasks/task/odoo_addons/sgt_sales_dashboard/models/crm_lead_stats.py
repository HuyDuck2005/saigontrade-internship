from odoo import models, fields, api
from datetime import datetime, timedelta

class CrmLeadStats(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def get_dashboard_stats(self, date_filter='all'):
        domain = [('type', '=', 'opportunity')]
        today = fields.Datetime.today()

        if date_filter == 'today':
            domain.append(('create_date', '>=', today.replace(hour=0, minute=0, second=0)))
        elif date_filter == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            domain.append(('create_date', '>=', start_of_week))
        elif date_filter == 'this_month':
            start_of_month = today.replace(day=1)
            domain.append(('create_date', '>=', start_of_month))
        elif date_filter == 'this_quarter':
            q_month = ((today.month - 1) // 3) * 3 + 1
            start_of_quarter = today.replace(month=q_month, day=1)
            domain.append(('create_date', '>=', start_of_quarter))
        elif date_filter == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            domain.append(('create_date', '>=', start_of_year))

        deals = self.search(domain)
        
        total_deals = len(deals)
        won_deals = len(deals.filtered(lambda d: d.stage_id.is_won))
        total_revenue = sum(deals.mapped('expected_revenue'))
        win_rate = round((won_deals / total_deals * 100), 1) if total_deals > 0 else 0.0

        stages = self.env['crm.stage'].search([])
        pipeline_labels = []
        pipeline_revenues = []
        for stage in stages:
            stage_deals = deals.filtered(lambda d: d.stage_id.id == stage.id)
            pipeline_labels.append(stage.name)
            pipeline_revenues.append(sum(stage_deals.mapped('expected_revenue')))

        source_labels = []
        source_counts = []
        for deal in deals:
            source_name = deal.source_id.name if deal.source_id else 'Trực tiếp / Khác'
            if source_name in source_labels:
                idx = source_labels.index(source_name)
                source_counts[idx] += 1
            else:
                source_labels.append(source_name)
                source_counts.append(1)

        return {
            'kpi': {
                'total_deals': total_deals,
                'total_revenue': f"{total_revenue:,.0f} đ",
                'won_deals': won_deals,
                'win_rate': f"{win_rate}%"
            },
            'charts': {
                'pipeline_labels': pipeline_labels,
                'pipeline_revenues': pipeline_revenues,
                'source_labels': source_labels,
                'source_counts': source_counts,
            }
        }
