# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2020 GTECH,LLC <vk.3141592653@gmail.com>

{
    'name': 'Customer Invoice with Product Images (XLSX)',
    'version': '1.0.0',
    'category': 'Extra Tools',
    'summary': 'Customer Invoice with Product Images (XLSX)',     
    'price': 0.00,
    'currency': 'EUR',
    "license": "OPL-1",     
    'description': """
Customer Invoice with Product Images (XLSX)
====================================
Customer Invoice with Product Images in MS Excel format (XLSX)
Generate the Excel Report from a Template.
Report for Report Designer (XLSX, XLSM). 
    Odoo Report XLSX  Create Excel Report Excel Reports Accounting Reports Financial Report Financial Reports Stock Reports Inventory Reports \
    Dynamic Sale Analysis Reports Export Excel Export xlsx Project Reports Warehouse Reports Purchases Reports Marketing Reports Sales Reports \
    Report Designer Reports Designer Report Builder Reports Builder Product Report Customer Report POS Reports POS Report Analysis Report \
    BI Report BI Reports BI Business Intelligence Report Business Intelligence Reports BI Analytics BI Analytic Data Analysis Reporting Tool
    """,
    'author': 'GTECH',
    'support': 'vk.3141592653@gmail.com',
    'depends': ['account'],
    'images': ['static/description/banner_rep.png'],
    'data': [
        'data/customer_invoice_with_product_images_xlsx.xml',
    ],
    'qweb': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    "pre_init_hook": "pre_init_check",
}
