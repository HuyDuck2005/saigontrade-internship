import json
import re
import base64
import time
from datetime import date
from odoo import http, fields
from odoo.http import request

# Bộ nhớ tạm in-memory cho Rate Limiting theo địa chỉ IP
IP_SUBMISSION_TRACKER = {}

class LeadPortalController(http.Controller):
    
    def _check_rate_limit(self, ip_address, limit=5, window=600):
        """Giới hạn tối đa `limit` lượt gửi trong `window` giây cho mỗi IP"""
        now = time.time()
        records = IP_SUBMISSION_TRACKER.get(ip_address, [])
        # Lọc các lượt gửi nằm trong khung thời gian
        records = [t for t in records if now - t < window]
        if len(records) >= limit:
            return False
        records.append(now)
        IP_SUBMISSION_TRACKER[ip_address] = records
        return True

    @http.route('/leads', auth='public', website=True, sitemap=True)
    def leads_list(self, **kwargs):
        category_id = kwargs.get('category_id')
        country = kwargs.get('country')
        search_query = kwargs.get('search')
        intent = kwargs.get('intent')
        verified_only = kwargs.get('verified')
        page = int(kwargs.get('page', 1))
        per_page = 12
        today = date.today()
        
        domain = [
            ('approval_status', '=', 'approved'),
            ('website_visible', '=', True),
            '|', ('expiration_date', '=', False), ('expiration_date', '>=', today)
        ]
        
        if intent:
            domain.append(('lead_intent', '=', intent))
        if category_id:
            domain.append(('lead_category', '=', int(category_id)))
        if country:
            domain.append(('country_region', 'ilike', country))
        if search_query:
            domain.append(('name', 'ilike', search_query))
        if verified_only == '1':
            domain.append(('is_verified', '=', True))
        
        leads = request.env['crm.lead'].sudo().search(domain, order='website_published_date desc')
        total = len(leads)
        
        featured_leads = request.env['crm.lead'].sudo().search([
            ('approval_status', '=', 'approved'),
            ('website_visible', '=', True),
            '|', ('expiration_date', '=', False), ('expiration_date', '>=', today)
        ], limit=12, order='website_view_count desc')

        categories = request.env['lead.category'].sudo().search([])
        countries = request.env['crm.lead'].sudo().search([('approval_status', '=', 'approved')]).mapped('country_region')
        
        return request.render('website_lead_showcase.leads_list', {
            'leads': leads[((page - 1) * per_page):(page * per_page)],
            'featured_leads': featured_leads,
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
            'verified_only': verified_only,
        })
    
    @http.route('/leads/<int:lead_id>', auth='public', website=True)
    def lead_detail(self, lead_id, **kwargs):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        today = date.today()
        if not lead.exists() or lead.approval_status != 'approved' or not lead.website_visible:
            return request.redirect('/leads')
        if lead.expiration_date and lead.expiration_date < today:
            return request.redirect('/leads')
        
        lead.sudo().website_view_count += 1
        
        domain_company = [
            ('approval_status', '=', 'approved'),
            ('website_visible', '=', True),
            ('id', '!=', lead_id),
            '|', ('expiration_date', '=', False), ('expiration_date', '>=', today)
        ]
        if lead.partner_name:
            domain_company.append(('partner_name', '=', lead.partner_name))
        elif lead.lead_category:
            domain_company.append(('lead_category', '=', lead.lead_category.id))

        company_deals = request.env['crm.lead'].sudo().search(domain_company, limit=6)
        
        related_leads = request.env['crm.lead'].sudo().search([
            ('approval_status', '=', 'approved'),
            ('website_visible', '=', True),
            ('lead_category', '=', lead.lead_category.id if lead.lead_category else False),
            ('id', '!=', lead_id),
            '|', ('expiration_date', '=', False), ('expiration_date', '>=', today)
        ], limit=4)
        
        return request.render('website_lead_showcase.lead_detail', {
            'lead': lead,
            'company_deals': company_deals,
            'related_leads': related_leads,
        })

    @http.route('/leads/<int:lead_id>/download_brochure', auth='public', website=True)
    def download_brochure(self, lead_id, **kwargs):
        """Tải tài liệu hồ sơ năng lực / catalogue PDF"""
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or not lead.brochure_file:
            return request.not_found()
        
        filecontent = base64.b64decode(lead.brochure_file)
        filename = lead.brochure_filename or f"Catalogue_Deal_{lead.id}.pdf"
        return request.make_response(filecontent, [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename="{filename}"')
        ])

    @http.route('/leads/<int:lead_id>/contact', type='http', auth='public', methods=['POST'], csrf=False)
    def lead_contact(self, lead_id, **kwargs):
        ip = request.httprequest.remote_addr or '127.0.0.1'
        if not self._check_rate_limit(ip):
            return request.make_response(json.dumps({
                'status': 'error', 
                'message': 'Bạn đã gửi yêu cầu quá nhiều lần. Vui lòng chờ 10 phút!'
            }), headers=[('Content-Type', 'application/json')])

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.approval_status != 'approved':
            return request.make_response(json.dumps({'status': 'error', 'message': 'Không tìm thấy thông tin cơ hội.'}), headers=[('Content-Type', 'application/json')])
        
        contact_name = kwargs.get('contact_name', '').strip()
        contact_email = kwargs.get('contact_email', '').strip()
        contact_phone = kwargs.get('contact_phone', '').strip()
        message = kwargs.get('message', '').strip()
        selected_deal_ids = kwargs.get('selected_deals', '')
        
        if not all([contact_name, contact_email, message]):
            return request.make_response(json.dumps({'status': 'error', 'message': 'Vui lòng điền đầy đủ các thông tin bắt buộc!'}), headers=[('Content-Type', 'application/json')])
        
        # Regex kiểm tra Email & Số điện thoại
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, contact_email):
            return request.make_response(json.dumps({'status': 'error', 'message': 'Địa chỉ email không đúng định dạng!'}), headers=[('Content-Type', 'application/json')])
            
        if contact_phone and not re.match(r'^(0|\+84)[0-9]{8,11}$', re.sub(r'[\s\.\-]', '', contact_phone)):
            return request.make_response(json.dumps({'status': 'error', 'message': 'Số điện thoại không hợp lệ (cần từ 9-11 chữ số)!'}), headers=[('Content-Type', 'application/json')])

        full_message = f"Lời nhắn: {message}\n"
        if selected_deal_ids:
            deal_ids = [int(i.strip()) for i in selected_deal_ids.split(',') if i.strip().isdigit()]
            if deal_ids:
                extra_deals = request.env['crm.lead'].sudo().browse(deal_ids)
                deal_titles = ", ".join(extra_deals.mapped('name'))
                full_message += f"\n[Các Deal kết nối gộp]:\n- {deal_titles}"

        new_lead = request.env['crm.lead'].sudo().create({
            'name': f"[SAIGONTRADE KẾT NỐI] {contact_name} -> {lead.name}",
            'email_from': contact_email,
            'phone': contact_phone,
            'description': full_message,
            'type': 'opportunity',
            'referred_lead_id': lead.id,
            'approval_status': 'draft',
            'website_visible': False,
        })
        lead.sudo().website_contact_count += 1
        
        template = request.env.ref('website_lead_showcase.email_lead_inquiry', raise_if_not_found=False)
        if template:
            template.sudo().send_mail(new_lead.id, force_send=False)
            
        return request.make_response(json.dumps({
            'status': 'success',
            'message': 'Yêu cầu kết nối giao thương đã gửi thành công! Chuyên viên xúc tiến SaiGonTrade sẽ liên hệ bạn ngay.'
        }), headers=[('Content-Type', 'application/json')])

    # ===== CỔNG DOANH NGHIỆP TỰ ĐĂNG TIN (/leads/submit) =====
    @http.route('/leads/submit', auth='public', website=True)
    def lead_submit_portal(self, **kwargs):
        categories = request.env['lead.category'].sudo().search([])
        return request.render('website_lead_showcase.lead_submit_form', {
            'categories': categories
        })

    @http.route('/leads/submit/process', type='http', auth='public', methods=['POST'], csrf=False)
    def lead_submit_process(self, **kwargs):
        ip = request.httprequest.remote_addr or '127.0.0.1'
        if not self._check_rate_limit(ip):
            return request.make_response(json.dumps({
                'status': 'error', 
                'message': 'Bạn đã gửi yêu cầu quá nhiều lần. Vui lòng thử lại sau 10 phút!'
            }), headers=[('Content-Type', 'application/json')])

        name = kwargs.get('title', '').strip()
        partner_name = kwargs.get('company_name', '').strip()
        intent = kwargs.get('intent', 'sell')
        category_id = kwargs.get('category_id')
        country = kwargs.get('country', 'Việt Nam').strip()
        contact_person = kwargs.get('contact_name', '').strip()
        contact_email = kwargs.get('contact_email', '').strip()
        contact_phone = kwargs.get('contact_phone', '').strip()
        short_description = kwargs.get('short_description', '').strip()
        description = kwargs.get('description', '').strip()

        if not all([name, partner_name, contact_email, contact_person, short_description]):
            return request.make_response(json.dumps({'status': 'error', 'message': 'Vui lòng điền đầy đủ các thông tin có dấu sao (*)'}), headers=[('Content-Type', 'application/json')])

        vals = {
            'name': name,
            'partner_name': partner_name,
            'type': 'opportunity',
            'lead_intent': intent,
            'lead_category': int(category_id) if category_id else False,
            'country_region': country,
            'contact_person': contact_person,
            'contact_email': contact_email,
            'contact_phone': contact_phone,
            'short_description': short_description,
            'description': description,
            'approval_status': 'draft',
            'website_visible': False,
        }

        # Đọc ảnh đính kèm nếu có
        image_file = request.httprequest.files.get('lead_image')
        if image_file:
            vals['lead_image'] = base64.b64encode(image_file.read())

        # Đọc catalogue PDF đính kèm nếu có
        brochure = request.httprequest.files.get('brochure_file')
        if brochure:
            vals['brochure_file'] = base64.b64encode(brochure.read())
            vals['brochure_filename'] = brochure.filename

        request.env['crm.lead'].sudo().create(vals)

        return request.make_response(json.dumps({
            'status': 'success',
            'message': 'Đăng tin giao thương thành công! Đội ngũ kiểm duyệt SaiGonTrade sẽ xét duyệt và thông báo qua email của bạn.'
        }), headers=[('Content-Type', 'application/json')])
