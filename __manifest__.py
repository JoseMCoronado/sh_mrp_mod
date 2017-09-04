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

    'depends':['base','purchase','stock','sale','mrp'],
    'data':[
            'views/mrp_entry_wizard_views.xml',
            'views/sale_order_views.xml',
            'views/mrp_views.xml',
            ],
    'installable': True,
}
