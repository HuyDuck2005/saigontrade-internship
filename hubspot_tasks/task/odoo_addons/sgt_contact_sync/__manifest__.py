{
    'name': 'SGT Contact Dual-Write Sync',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Thêm nút bấm đồng bộ Contact thủ công sang Odoo 2',
    'depends': ['base', 'contacts'],
    'data': [
        'views/partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
