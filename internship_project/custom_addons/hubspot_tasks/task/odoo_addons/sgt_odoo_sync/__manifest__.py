{
    'name': 'SGT Odoo1 to Odoo2 Sync Contact',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Đồng bộ Contact từ CRM Lead Odoo1 sang Odoo2 qua XML-RPC',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/sgt_remote_odoo_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
