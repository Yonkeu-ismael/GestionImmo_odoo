# -*- coding: utf-8 -*-
# By IsmaDev
# Create from 25/01/2024

{
    'name': "Immo",
    'version': '1.0',
    'depends': ['base'],
    'author': "IsmaDev Cam",
    'category': 'Immobilier',
    'description': """
    Ce nouveau module couvre un domaine d'activité très spécifique et donc non inclus dans l'ensemble standard des modules Odoo : L'immobilier

    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/property_type_views.xml',
        'views/property_tag_views.xml',
        'views/property_offer_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',


    ],
    # data files containing optionally loaded demonstration data
    'demo': [
       # 'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,

}