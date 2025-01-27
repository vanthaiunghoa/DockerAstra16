# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Purchase Order Link",
    "summary": "Link between picking and purchase order",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Astratech",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "application": False,
    "installable": True,
    "depends": ["purchase_stock"],
    "data": ["views/stock_picking_view.xml"],
}
