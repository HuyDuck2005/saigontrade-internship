import xmlrpc.client
import logging
from typing import Dict, Any, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Task7_FieldMapper")

# Bảng mapping chi tiết theo yêu cầu đề bài Task 7
FIELD_MAPPING_RULES = {
    'x_firstname': ('x_custome_fields_firstname', 'char', 'First Name'),
    'x_lastname': ('x_custome_fields_lastname', 'char', 'Last Name'),
    'x_mobilephone': ('x_custome_fields_mobilephone', 'char', 'Mobile Phone'),
    'x_jobtitle': ('x_custome_fields_jobtitle', 'char', 'Job Title'),
    'x_website': ('x_website', 'char', 'Website'),
    'x_salutation': ('x_custome_fields_salutation', 'char', 'Salutation'),
    'x_country': ('x_custome_fields_sgt_country', 'char', 'Country'),
    'x_getfly_id': ('x_id', 'char', 'Getfly ID'),
    'x_notes': ('x_custome_fields_notes', 'text', 'Notes'),
    'x_product_category': ('x_custome_fields_product_category', 'char', 'Product Category'),
    'x_product_details': ('x_custome_fields_product_details', 'text', 'Product Details'),
    'x_fb_industry': ('x_custome_fields_fb_industry', 'char', 'FB Industry'),
    'x_url_zalo_group': ('x_custome_fields_url_zalo_group', 'char', 'Zalo Group URL'),
    'x_url_whatsapp_group': ('x_custome_fields_url_whatsapp_group', 'char', 'WhatsApp Group URL'),
    'x_url_fb_profile': ('x_custome_fields_url_fb_profile', 'char', 'FB Profile URL'),
    'x_type_contact': ('x_custome_fields_type_contact', 'char', 'Contact Type'),
    'BD': ('x_expo', 'char', 'BD Expo'),
    'x_event': ('x_custome_fields_event', 'char', 'Event Name'),
    'x_event_location': ('x_custome_fields_event_location', 'char', 'Event Location'),
    'x_email_report': ('x_custome_fields_email_report', 'char', 'Email Report')
}

class OdooFieldMapper:
    def __init__(self, rpc_client, db: str, uid: int, password: str, target_model: str = 'res.partner'):
        self.rpc = rpc_client
        self.db = db
        self.uid = uid
        self.password = password
        self.target_model = target_model
        self.existing_remote_fields = set()
        self._load_remote_fields()

    def _load_remote_fields(self):
        """Lấy danh sách các trường hiện có trên target model của Odoo 2."""
        try:
            fields_dict = self.rpc.execute_kw(
                self.db, self.uid, self.password,
                self.target_model, 'fields_get',
                [], {'attributes': ['type', 'string']}
            )
            self.existing_remote_fields = set(fields_dict.keys())
        except Exception as e:
            logger.warning(f"Không thể đọc metadata trường từ Odoo 2: {e}")

    def ensure_remote_custom_field(self, field_name: str, field_type: str, field_label: str):
        """Yêu cầu nâng cao: Tự động khởi tạo Custom Field trên Odoo 2 nếu chưa tồn tại."""
        if field_name in self.existing_remote_fields:
            return True

        try:
            model_ids = self.rpc.execute_kw(
                self.db, self.uid, self.password,
                'ir.model', 'search',
                [[['model', '=', self.target_model]]]
            )
            if not model_ids:
                return False

            self.rpc.execute_kw(
                self.db, self.uid, self.password,
                'ir.model.fields', 'create',
                [{
                    'name': field_name,
                    'model_id': model_ids[0],
                    'ttype': field_type,
                    'field_description': field_label,
                    'state': 'manual'
                }]
            )
            logger.info(f"✨ [Tự động tạo trường] Đã tạo custom field '{field_name}' ({field_type}) trên Odoo 2 ({self.target_model})")
            self.existing_remote_fields.add(field_name)
            return True
        except Exception as e:
            logger.warning(f"Không thể tự tạo field '{field_name}' trên Odoo 2: {e}")
            return False

    def map_and_sanitize(self, source_lead_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Ánh xạ dữ liệu và lọc an toàn các field hợp lệ."""
        mapped_vals = {}
        report_log = {}

        # 1. Map các trường tiêu chuẩn cơ bản
        if source_lead_data.get('name') or source_lead_data.get('contact_name'):
            mapped_vals['name'] = source_lead_data.get('contact_name') or source_lead_data.get('name')
        if source_lead_data.get('phone'):
            mapped_vals['phone'] = str(source_lead_data.get('phone')).strip()
        if source_lead_data.get('email_from') or source_lead_data.get('email'):
            mapped_vals['email'] = str(source_lead_data.get('email_from') or source_lead_data.get('email')).strip()

        # 2. Map các custom field theo bộ quy tắc
        for src_field, (tgt_field, f_type, label) in FIELD_MAPPING_RULES.items():
            val = source_lead_data.get(src_field)
            if val is not None and str(val).strip() != '':
                # Đảm bảo field tồn tại trên Odoo 2 trước khi ghi
                self.ensure_remote_custom_field(tgt_field, f_type, label)
                if tgt_field in self.existing_remote_fields:
                    mapped_vals[tgt_field] = str(val).strip()
                    report_log[src_field] = f"Mapped -> {tgt_field} ('{val}')"
                else:
                    report_log[src_field] = f"Skipped (Field {tgt_field} not found on Odoo 2)"

        return mapped_vals, report_log
