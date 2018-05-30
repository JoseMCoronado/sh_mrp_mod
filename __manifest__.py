# -*- coding: utf-8 -*-
{
    'name': 'Commissioned Manufacturing Modifications',
    'category': 'Purchase',
    'author': 'GFP Solutions',
    'summary': 'Custom',
    'version': '1.0',
    'description': """
Manufacturing modifications commissioned by Speedhut. Check Flow for modification details.

THIS MODULE IS PROVIDED AS IS - INSTALLATION AT USERS' OWN RISK - AUTHOR OF MODULE DOES NOT CLAIM ANY
RESPONSIBILITY FOR ANY BEHAVIOR ONCE INSTALLED.
        """,

    'depends':['base','purchase','stock','sale','mrp','sale_order_dates', 'sh_line_attribute'],
    'data':[
            'views/ir_sequence.xml',
            'views/mrp_entry_wizard_views.xml',
            'views/sale_order_views.xml',
            'views/mrp_views.xml',
            'views/sale_workorder_views.xml',
            'views/product_template_views.xml',
            'views/ir_model_access.xml',
            'views/ir_ui_qweb.xml',
            'views/ir_ui_views.xml',
            ],
    'installable': True,
}
