import json
from odoo import http, fields
from odoo.http import request

class LeadPortalController(http.Controller):
    
    @http.route('/leads', auth='public', website=True, sitemap=True)
    def leads_list(self, **kwargs):
        category_id = kwargs.get('category_id')
        country = kwargs.get('country')
        search_query = kwargs.get('search')
        intent = kwargs.get('intent')
        page = int(kwargs.get('page', 1))
        per_page = 12
        
        domain = [('approval_status', '=', 'approved'), ('website_visible', '=', True)]
        
        if intent:
            domain.append(('lead_intent', '=', intent))
        if category_id:
            domain.append(('lead_category', '=', int(category_id)))
        if country:
            domain.append(('country_region', 'ilike', country))
        if search_query:
            domain.append(('name', 'ilike', search_query))
        
        leads = request.env['crm.lead'].sudo().search(domain, order='website_published_date desc')
        total = len(leads)
        
        categories = request.env['lead.category'].sudo().search([])
        countries = request.env['crm.lead'].sudo().search([('approval_status', '=', 'approved')]).mapped('country_region')
        
        return request.render('website_lead_showcase.leads_list', {
            'leads': leads[((page - 1) * per_page):(page * per_page)],
            'categories': categories,
            'countries': sorted(list(set([c for c in countries if c]))),
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if per_page else 1,
            'search_query': search_query,
            'selected_category': category_id,
            'selected_country': country,
            'selected_intent': intent,
        })
    
    @http.route('/leads/<int:lead_id>', auth='public', website=True)
    def lead_detail(self, lead_id, **kwargs):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.approval_status != 'approved' or not lead.website_visible:
            return request.redirect('/leads')
        
        lead.sudo().website_view_count += 1
        related_leads = request.env['crm.lead'].sudo().search([
            ('approval_status', '=', 'approved'), ('website_visible', '=', True),
            ('lead_category', '=', lead.lead_category.id), ('id', '!=', lead_id)
        ], limit=4)
        
        return request.render('website_lead_showcase.lead_detail', {
            'lead': lead,
            'related_leads': related_leads,
        })
    
    @http.route('/leads/<int:lead_id>/contact', type='http', auth='public', methods=['POST'], csrf=False)
    def lead_contact(self, lead_id, **kwargs):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.approval_status != 'approved':
            return request.make_response(json.dumps({'status': 'error', 'message': 'Lead not found'}), headers=[('Content-Type', 'application/json')])
        
        contact_name = kwargs.get('contact_name')
        contact_email = kwargs.get('contact_email')
        contact_phone = kwargs.get('contact_phone', '')
        message = kwargs.get('message')
        
        if not all([contact_name, contact_email, message]):
            return request.make_response(json.dumps({'status': 'error', 'message': 'Thiếu thông tin bắt buộc!'}), headers=[('Content-Type', 'application/json')])
        
        new_lead = request.env['crm.lead'].sudo().create({
            'name': f"[YÊU CẦU KẾT NỐI] {contact_name} -> {lead.name}",
            'email_from': contact_email,
            'phone': contact_phone,
            'description': message,
            'type': 'opportunity',
            'referred_lead_id': lead.id,
            'approval_status': 'draft',
            'website_visible': False,
        })
        lead.sudo().website_contact_count += 1
        
        template = request.env.ref('website_lead_showcase.email_lead_inquiry', raise_if_not_found=False)
        if template:
            template.sudo().send_mail(new_lead.id, force_send=False)
            
        return request.make_response(json.dumps({'status': 'success', 'message': 'Cảm ơn! Chúng tôi sẽ liên hệ với bạn sớm nhất.'}), headers=[('Content-Type', 'application/json')])
