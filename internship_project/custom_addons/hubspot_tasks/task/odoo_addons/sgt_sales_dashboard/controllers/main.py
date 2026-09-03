from odoo import http
from odoo.http import request

class SgdSalesDashboardController(http.Controller):
    @http.route('/api/dashboard/export_csv', type='http', auth='user')
    def export_sales_csv(self, **kwargs):
        return "Tính năng xuất CSV đang được nâng cấp."
