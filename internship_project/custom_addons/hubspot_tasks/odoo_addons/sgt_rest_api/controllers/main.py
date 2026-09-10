from odoo import http
from odoo.http import request

class SGTAPIController(http.Controller):

    # TASK 11: SOCIAL CRM DEAL
    @http.route('/api/social_deal/create', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def create_social_deal(self, **kwargs):
        if not kwargs:
            return {"success": False, "error": "Không có dữ liệu payload."}
            
        deal_name = kwargs.get('deal_name')
        if not deal_name:
            return {"success": False, "error": "Thiếu trường bắt buộc: deal_name"}
            
        lead_vals = {
            'name': deal_name,
            'contact_name': kwargs.get('contact_name'),
            'phone': kwargs.get('phone'),
            'email_from': kwargs.get('email'),
            'x_social_platform': kwargs.get('x_social_platform'),
            'x_social_profile_name': kwargs.get('x_social_profile_name'),
            'x_social_profile_url': kwargs.get('x_social_profile_url'),
            'x_social_post_text': kwargs.get('x_social_post_text'),
        }
        
        try:
            lead = request.env['crm.lead'].sudo().create(lead_vals)
            return {"success": True, "lead_id": lead.id, "message": "Tạo Social CRM Deal thành công!"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # TASK 12: ATTACHMENT UPLOAD
    @http.route('/api/attachment/upload', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def upload_attachment(self, **kwargs):
        lead_id = kwargs.get('lead_id')
        filename = kwargs.get('filename')
        image_base64 = kwargs.get('image_base64')
        mimetype = kwargs.get('mimetype')
        
        if not all([lead_id, filename, image_base64, mimetype]):
            return {"success": False, "error": "Thiếu các trường bắt buộc (lead_id, filename, image_base64, mimetype)."}
            
        # Validate MIME type
        allowed_mimes = ['image/png', 'image/jpeg', 'application/pdf']
        if mimetype not in allowed_mimes:
            return {"success": False, "error": "Chỉ hỗ trợ file PNG, JPEG, PDF."}
            
        # Validate Size (Giới hạn 10MB)
        padding = image_base64.count('=')
        size_in_bytes = (len(image_base64) * 3 / 4) - padding
        if size_in_bytes > 10 * 1024 * 1024:
            return {"success": False, "error": "Dung lượng file vượt quá 10MB."}
            
        try:
            lead = request.env['crm.lead'].sudo().search([('id', '=', lead_id)])
            if not lead:
                return {"success": False, "error": "Không tìm thấy CRM Deal ID tương ứng."}
                
            attachment = request.env['ir.attachment'].sudo().create({
                'name': filename,
                'type': 'binary',
                'datas': image_base64,
                'res_model': 'crm.lead',
                'res_id': lead_id,
                'mimetype': mimetype
            })
            return {"success": True, "attachment_id": attachment.id, "message": "Upload file đính kèm thành công!"}
        except Exception as e:
            return {"success": False, "error": str(e)}
