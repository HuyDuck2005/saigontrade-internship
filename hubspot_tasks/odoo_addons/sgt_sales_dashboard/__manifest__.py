{
    'name': 'SGT CRM BI Dashboard (OWL)',
    'version': '5.0',
    'category': 'Sales/CRM',
    'summary': 'Dashboard phân tích tương tác động xây dựng bằng OWL',
    'depends': ['base', 'crm', 'web'],
    'data': [
        'views/dashboard_menu.xml',
        'views/bi_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sgt_sales_dashboard/static/src/components/dashboard.js',
            'sgt_sales_dashboard/static/src/components/dashboard.xml',
            'sgt_sales_dashboard/static/src/scss/dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
