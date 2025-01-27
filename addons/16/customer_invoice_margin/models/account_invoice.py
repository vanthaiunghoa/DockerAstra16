# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    margin_amount = fields.Char(compute='_get_average_margin_percentage', string='Margin Amount')
    margin_amount_local_currency = fields.Char(compute='_get_average_margin_percentage', string='Local Margin Amount')
    margin_percentage = fields.Char(compute='_get_average_margin_percentage', string='Margin Percentage')

    @api.depends('invoice_line_ids','invoice_line_ids.quantity','invoice_line_ids.price_unit', 'invoice_line_ids.discount', 'invoice_line_ids.currency_id')
    def _get_average_margin_percentage(self):
        sale_price = discount = cost = margin_amount = 0.0
        line_cost = line_margin_amount = margin_percentage = 0.0
        for record in self:
            if record.invoice_line_ids:
                for line in record.invoice_line_ids:
                    sale_price = line.price_unit * line.quantity
                    discount = (sale_price * line.discount)/100
                    cost = line.product_id.standard_price * line.quantity

                    from_currency = line.product_id.cost_currency_id

                    cost = from_currency._convert(
                        from_amount=cost,
                        to_currency=record.currency_id,
                        company=record.company_id or self.env.company,
                        date=record.invoice_date or fields.Date.context_today(self),
                        round=False,
                    )
                    line_cost += cost
                    margin_amount = (sale_price - discount) - cost
                    line_margin_amount += margin_amount
                if line_cost:
                    margin_percentage = (line_margin_amount / line_cost) * 100
                else:
                    margin_percentage = 100
                record.margin_amount = round(line_margin_amount,2)
                record.margin_amount_local_currency = round(record.currency_id._convert(
                    from_amount=line_margin_amount,
                    to_currency=record.company_currency_id,
                    company=record.company_id or self.env.company,
                    date=record.invoice_date or fields.Date.context_today(self),
                    round=False,
                    ), 2)
                record.margin_percentage = str(round(margin_percentage,2)) + '%'
            else:
                record.margin_amount = ''
                record.margin_amount_local_currency = ''
                record.margin_percentage = ''

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    margin_percentage = fields.Char(compute='_get_total_percentage', string='Margin Percentage')

    @api.depends('quantity','price_unit', 'discount', 'currency_id')
    def _get_total_percentage(self):
        sale_price = discount = cost = margin_amount = margin_percentage = 0.0
        for record in self:
            if record.product_id:
                sale_price = record.price_unit * record.quantity
                discount = (sale_price*record.discount)/100
                cost = record.product_id.standard_price * record.quantity
                
                from_currency = record.product_id.cost_currency_id

                cost = from_currency._convert(
                    from_amount=cost,
                    to_currency=record.move_id.currency_id,
                    company=record.move_id.company_id or self.env.company,
                    date=record.move_id.invoice_date or fields.Date.context_today(self),
                    round=False,
                )

                margin_amount = (sale_price - discount) - cost
                if cost:
                    margin_percentage = (margin_amount / cost) * 100 
                else:
                    margin_percentage = 100 
                record.margin_percentage = str(round(margin_percentage,2)) + ' %'
            else:
                record.margin_percentage = ''
