# -*- coding: utf-8 -*-
{
    'name': "Aruna Odoo Test",

    'summary': """
        A simple game made for Aruna Odoo Test. """,

    'description': """
        A simple game made for Aruna Odoo Test.
    """,

    'author': "Hersyanda Putra Adi",
    'website': "http://www.hrsynd.site",
    'category': 'Uncategorized',
    'application': True,
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
