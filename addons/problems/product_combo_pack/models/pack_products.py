# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Afras Habis (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PackProducts(models.Model):
    _name = 'pack.products'
    _rec_name = 'product_tmpl_id'
    _description = 'Select Pack Products'

    product_id = fields.Many2one('product.product', string='Product', required=True,
                                 domain=[('is_pack', '=', False)])
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    price = fields.Float('Price', compute='compute_price', store=True)
    quantity = fields.Integer('Quantity', default=1)
    qty_available = fields.Float('Quantity Available', compute='compute_quantity_of_product', store=True,
                                 readonly=False)
    total_available_quantity = fields.Float('Total Quantity')

    @api.depends('product_id', 'total_available_quantity', 'product_id.qty_available')
    def compute_quantity_of_product(self):
        for record in self:
            location_id = record.product_tmpl_id.pack_location_id
            if location_id:
                stock_quant = self.env['stock.quant'].search(
                    [('product_id', '=', record.product_id.id), ('location_id', '=', location_id.id)])
                if stock_quant:
                    record.qty_available = stock_quant.quantity
                else:
                    record.qty_available = False
            else:
                record.qty_available = False

    @api.depends('product_id', 'quantity')
    def compute_price(self):
        for record in self:
            record.price = record.product_id.lst_price * record.quantity

    @api.onchange('quantity')
    def set_price(self):
        self.price = self.product_id.lst_price * self.quantity

    @api.constrains('quantity')
    def _check_positive_qty(self):
        if any([ml.quantity < 0 for ml in self]):
            raise ValidationError(_('You can not enter negative quantities.'))
