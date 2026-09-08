{
    'name': 'SGT Odoo1 to Odoo2 Sync Contact',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Đồng bộ Contact & Dynamic Mapping Odoo1 sang Odoo2',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/sgt_remote_odoo_views.xml',
        'views/sync_config_views.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
        'views/sync_log_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
