# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
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

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def _onchange_partner_id_warning(self):
        result = super(SaleOrder, self)._onchange_partner_id_warning()
        if not self.partner_id:
            self.update({
                'warehouse_id': False,
            })
        warehouse = False
        if self.partner_id.warehouse_id:
            warehouse = self.partner_id.warehouse_id
        else:
            if self.partner_id.parent_id:
                warehouse = self.partner_id.parent_id.warehouse_id
        values = {
                'warehouse_id': warehouse,
        }
        self.update(values)
        return result



       









