from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website

class WebsiteLeadRedirect(Website):
    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        # Ép chuyển hướng từ trang chủ trắng tinh sang trang danh sách Lead
        return request.redirect('/leads')
