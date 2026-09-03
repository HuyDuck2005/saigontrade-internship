from odoo import http
from odoo.http import request

class SGTDashboardAPI(http.Controller):
    @http.route('/api/sgt_dashboard/get_kpis', type='json', auth='user')
    def get_kpis(self, date_from=None, date_to=None):
        domain = [('type', '=', 'opportunity')]
        if date_from:
            domain.append(('create_date', '>=', date_from))
        if date_to:
            domain.append(('create_date', '<=', date_to))

        deals = request.env['crm.lead'].search(domain)
        total_opportunities = len(deals)
        expected_revenue = sum(deals.mapped('expected_revenue'))
        won_deals = len(deals.filtered(lambda d: d.probability == 100))
        conversion_rate = (won_deals / total_opportunities * 100) if total_opportunities > 0 else 0.0

        stages = request.env['crm.stage'].search([])
        stage_labels = [s.name for s in stages]
        stage_revenues = [sum(deals.filtered(lambda d: d.stage_id.id == s.id).mapped('expected_revenue')) for s in stages]

        source_data = {}
        for deal in deals:
            source_name = deal.source_id.name if deal.source_id else 'Khác / Trực tiếp'
            source_data[source_name] = source_data.get(source_name, 0) + 1

        return {
            'kpi': {
                'total_opportunities': total_opportunities,
                'expected_revenue': expected_revenue,
                'won_deals': won_deals,
                'conversion_rate': round(conversion_rate, 2)
            },
            'charts': {
                'stage_labels': stage_labels,
                'stage_revenues': stage_revenues,
                'source_labels': list(source_data.keys()),
                'source_counts': list(source_data.values())
            }
        }
