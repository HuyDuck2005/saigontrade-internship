{
    'name': 'SGT Sales Utilities',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Export Excel and Approval Workflow for CRM',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/export_deal_wizard_views.xml',
        'views/crm_lead_approval_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
