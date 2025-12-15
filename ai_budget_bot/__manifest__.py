{
    'name': 'AI Budget Chatbot',
    'version': '13.0.1.0.0',
    'summary': 'AI chatbot for budget insights',
    'author': 'Taha Chelly',
    'category': 'Tools',
    'depends': ['web', 'ccit_groups_config', 'om_account_budget', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_budget_chat_wizard_views.xml',
        'views/assets.xml',
        'views/ai_chat_action.xml',
        'views/ai_chat_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/ai_budget_bot/static/src/js/ai_chat.js',
            '/ai_budget_bot/static/src/css/ai_chat.css',
        ],
    },
    'installable': True,
    'application': False,
}