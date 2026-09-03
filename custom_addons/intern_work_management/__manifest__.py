{
    'name': 'Intern Work Management',
    'version': '1.0',
    'depends': ['base', 'project', 'hr', 'calendar', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'views/dashboard_views.xml',
        'views/daily_report_views.xml',
        'views/weekly_report_views.xml',
        'views/task_presentation_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}
