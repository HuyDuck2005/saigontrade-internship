{
    'name': 'SGT B2B Match Making',
    'version': '1.0',
    'summary': 'Task 19: Quản lý kết nối giữa hai doanh nghiệp',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/mm_lead_views.xml',
        'views/res_partner_match_views.xml',
    ],
    'installable': True,
    'application': True,
}
