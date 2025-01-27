{
    'name': 'Real Estate Sale',
    'version': '15.0.1.0.0',
    'summary': """Sell Real Estate Properties.""",
    'description': """This app helps to sell Real Estate Properties through website.""",
    'category': 'Accounting',
    'author': 'Astratech',
    'company': 'Zillo WebTech',
    'maintainer': 'Zillo WebTech',
    'website': 'https://www.nckwebtech.com/',
    'depends': ['account', 'product', 'base', 'sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/real_estate_field.xml',
        'report/inventory_product_report.xml',
        'report/inventory_product_template.xml',
        'views/product_template_real_estate.xml',
        'views/field_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
