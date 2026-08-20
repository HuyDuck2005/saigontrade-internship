{
    'name': 'SGT Batch Contact To CRM Deal Wizard',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Tạo Deal CRM hàng loạt từ danh sách Contact bằng Wizard',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_deal_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
