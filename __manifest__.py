# -*- coding: utf-8 -*-
{
    'name': "test_shopi",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",



    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sp_shop.xml',
        'views/shopify_shop.xml',
        'views/shopify_app.xml',
        'views/shop_app.xml',
         'views/res_config_settings_views.xml',
        'views/fetch_orders.xml',
        'views/shop_product.xml',
        'views/shop_orders.xml',
        'views/xero_redirect.xml',

        'views/xero_store.xml',
        'views/xero_model.xml',
        'views/table_history.xml',
        'views/invoice_record_history.xml',
        'views/shopify_discount.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
