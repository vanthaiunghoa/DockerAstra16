# Copyright 2019-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)

{
    "name": "Returns Management",
    "version": "16.0.1.1.0",
    "category": "Sales",
    "summary": """
        This application allows you to track your customers/vendors returns
         and grievances.
    """,
    "website": "https://sodexis.com/",
    'author': 'Astratech',
    "license": "OPL-1",
    "depends": [
        "crm",
        "sale",
        "purchase",
        "stock",
        "sale_stock",
    ],
    "data": [
        "security/crm_claim_rma_security.xml",
        "security/ir.model.access.csv",
        "views/crm_claim_view.xml",
        "views/crm_claim_team.xml",
        "views/crm_claim_menu.xml",
        "report/crm_claim_report_view.xml",
        "data/crm_claim_data.xml",
        "data/stock_data.xml",
        "views/res_partner_view.xml",
        "views/account_invoice_view.xml",
        "views/sale_view.xml",
        "views/purchase_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_inventory_view.xml",
        "views/stock_warehouse_views.xml",
        "wizard/stock_picking_return_view.xml",
        "wizard/account_invoice_refund_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "post_init_hook": "post_init_hook",
    "images": ["images/main_screenshot.png"],
}
