{
    'name': 'Website Lead Showcase',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'sequence': 1,
    'author': 'Your Company',
    'depends': ['website', 'crm', 'website_crm', 'sale_crm'],
    'installable': True,
    'application': False,
    'data': [
        'views/website_lead_gallery_template.xml',
        'views/crm_lead_gallery_views.xml',
        'security/security_gallery.xml',
        'security/security_image.xml',
        # Security
        'security/ir_model_access.xml',
        
        # Data
        'data/lead_category_data.xml',
        'data/test_lead_data.xml',
        
        # Views - Backend
        'views/crm_lead_views.xml',
        'views/dashboard_views.xml',
        
        # Views - Frontend
        'views/website_templates.xml',
        'views/email_templates.xml',
        'views/lead_reject_wizard_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_lead_showcase/static/css/lead_cards.css',
            'website_lead_showcase/static/js/lead_portal.js',
        ],
    },
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
}
