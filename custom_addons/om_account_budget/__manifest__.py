# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 13 Budget Management',
    'author': 'Odoo Mates, Odoo SA',
    'category': 'Accounting',
    'version': '13.0.2.1.0',
    'description': """Use budgets to compare actual with expected revenues and costs""",
    'summary': 'Odoo 13 Budget Management',
    'website': 'http://odoomates.tech',
    'depends': ['account','sale','purchase'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_depense_annuelle_views.xml',
        'views/report_position_budgetaire_views.xml',
        'views/pie_chart_depense_line_views.xml',
        'views/bar_chart_budget_line_views.xml',
        'views/report_chiffre_affaire_views.xml',
        'views/report_autonomie_views.xml',
        'views/report_ca_annee_views.xml',
        'views/assets.xml',
        'views/position_budgetaire_categorie_views.xml',
        'report/mail_template.xml',

    ],
    'assets': {
    'web.assets_backend': [
        'static/src/js/pivot_export_pdf.js',
        'static/src/js/graph_export_pdf.js',
        'static/src/js/jspdf.plugin.autotable.js',
        'static/src/js/jspdf.umd.min.js',
        'static/src/js/html2canvas.min.js',
    ],
},
    "images": ['static/description/banner.gif'],
    'demo': ['data/account_budget_demo.xml'],
}
