# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockLandedCostProductLine(models.Model):
    _name = 'pre.stock.landed.cost.product.lines'
    _description = 'Landed Cost Product Lines'

    def _default_currency(self):
        if self.product_id:
            return self.product_id.currency_id
        return self.env.company.currency_id

    cost_id = fields.Many2one(
        'pre.stock.landed.cost',
        string='Landed Cost',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=False,
    )
    description = fields.Char(
        string='Descripción',
        help='Nombre o descripción del producto',
    )
    quantity = fields.Float(
        string='Cantidad',
        required=True,
        default=1.0,
        help='Cantidad de productos especificados',
    )
    price_unit = fields.Monetary(
        string='Costo unitario USD',
        currency_field='currency_id',
        required=True,
        help='Costo unitario del producto según lo especificado en la pestaña de Productos',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=_default_currency
    )

    # Details
    total = fields.Float(
        string='Total USD',
        compute='_compute_total',
        store=True
    )
    item = fields.Integer(
        string="Item",
        compute="_compute_totals",
        readonly=True,
    )
    rate = fields.Float(
        string="Tasa USD",
        related="cost_id.rate",
        readonly=True,
        help='Tasa de cambio a la fecha de la pre liquidación (o según lo indicado)',
    )
    price_unit_usd = fields.Float(
        string="Total US$",
        compute="_compute_totals",
        readonly=True,
        help='Total de costo, según la cantidad indicada: “Qty” * “C/U US$”',
    )
    price_unit_rd = fields.Float(
        string="C/U RD",
        compute="_compute_totals",
        readonly=True,
        help='Costo unitario del producto según lo especificado en la pestaña de Productos',
    )
    amount_total_rd = fields.Float(
        string="Total RD",
        compute="_compute_totals",
        readonly=True,
        help='Total de costo, según la cantidad indicada: “Qty” * “C/U RD”',
    )
    factor = fields.Float(
        string="Factor",
        digits=(12, 3),
        compute="_compute_factor",
        readonly=True,
        help='Factor de costes en destino. Dado por el cálculo: ( “Total de costos adicionales” + “Total RD” ) / “Total USD”',
    )
    current_price_unit_rd = fields.Float(
        string="C/U Actual RD",
        compute="_compute_current_totals",
        readonly=True,
        help='Costo del producto luego de aplicar el factor de costos en destino. Dado por el cálculo: “C/U US$” * “Factor”',
    )
    current_total_rd = fields.Float(
        string="C/T Actual RD",
        compute="_compute_current_totals",
        readonly=True,
        help='Total de costo, según la cantidad indicada, luego de aplicar el factor de costos en destino',
    )
    current_price_unit_usd = fields.Float(
        string="C/U Actual US$",
        compute="_compute_current_totals",
        readonly=True,
        help='Costo del producto luego de aplicar el factor de costos en destino',
    )
    current_total_usd = fields.Float(
        string="C/T Actual US$",
        compute="_compute_current_totals",
        readonly=True,
        help='Total de costo, según la cantidad indicada, luego de aplicar el factor de costos en destino',
    )
    pvp_usd = fields.Float(
        string="PVP US$",
        default=lambda self: (self.product_id and (self.product_id.lst_price / self.cost_id.rate)) or 0.0,
        help='Precio de venta del producto según su registro, si el producto fue seleccionado de inventario.\n'
            'Si es un producto creado para la simulación, este valor debe especificarse',
    )
    pvp_rd = fields.Float(
        string="PVP RD",
        compute="_compute_pvp",
        compute_sudo=True,
        readonly=True,
        help='Precio de venta del producto según su registro, si el producto fue seleccionado de inventario. \n'
            'Si es un producto creado para la simulación, este valor debe especificarse',
    )
    margin = fields.Float(
        string="Margen %",
        compute="_compute_extra_indicators",
        readonly=True,
        help='Margen de ganancia expresado en valor porcentual. Dado por el cálculo: ( “PVP US$” – “C/U Actual US$” ) / “PVP US$”',
    )
    profit_usd = fields.Float(
        string="Ganancias en US$",
        compute="_compute_extra_indicators",
        readonly=True,
        help='Ganancia total obtenida por los productos según ajuste de costo y PVP. Dado por el cálculo: ( “PVP US$” – “C/U Actual US$” ) * “Qty”',
    )
    profit_rd = fields.Float(
        string="Ganancias en RD",
        compute="_compute_extra_indicators",
        readonly=True,
        help='Ganancia total obtenida por los productos según ajuste de costo y PVP. Dado por el cálculo: ( “PVP RD” – “C/U Actual RD” ) * “Qty”',
    )

    @api.depends('quantity', 'price_unit')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.standard_price / self.cost_id.rate
            self.description = self.product_id.display_name
        else:
            self.price_unit = 0.0
            self.description = None

        self.update({"price_unit": self.price_unit, "description": self.description})

    @api.depends('rate', 'price_unit', 'quantity')
    def _compute_totals(self):
        for item, record in enumerate(self, start=1):
            record.item = item
            record.price_unit_usd = record.price_unit * record.quantity
            record.price_unit_rd = record.price_unit * record.rate
            record.amount_total_rd = record.price_unit_rd * record.quantity

    @api.depends('cost_id', 'cost_id.amount_total')
    def _compute_factor(self):
        total_usd = sum(self.cost_id.product_lines.mapped('price_unit_usd'))
        total_rd = sum(self.cost_id.product_lines.mapped('amount_total_rd'))
        if total_usd:
            self.factor = (self.cost_id.amount_total + total_rd) / total_usd
        else:
            self.factor = 1.0

    @api.depends('price_unit', 'rate', 'factor', 'quantity')
    def _compute_current_totals(self):
        for record in self:
            record.current_price_unit_rd = record.price_unit * record.factor
            record.current_total_rd = record.current_price_unit_rd * record.quantity
            record.current_price_unit_usd = (
                record.current_price_unit_rd / record.rate
                if record.rate else 0.0
            )
            record.current_total_usd = record.current_price_unit_usd * record.quantity

    @api.depends('rate', 'pvp_usd')
    def _compute_pvp(self):
        for record in self:
            record.pvp_rd = record.pvp_usd * record.rate

    @api.depends('pvp_usd', 'pvp_rd', 'current_price_unit_usd', 'current_price_unit_rd', 'quantity')
    def _compute_extra_indicators(self):
        for record in self:
            if record.pvp_usd:
                record.margin = (record.pvp_usd - record.current_price_unit_usd) * 100 / record.pvp_usd
            else:
                record.margin = 0.0
            record.profit_usd = (record.pvp_usd - record.current_price_unit_usd) * record.quantity
            record.profit_rd = (record.pvp_rd - record.current_price_unit_rd) * record.quantity

    def get_lst_price_from_product(self, vals):
        pvp_usd = vals.get('pvp_usd')
        cost_id = vals.get('cost_id')
        product_id = vals.get('product_id')

        if not pvp_usd:
            if product_id:
                cost_id = self.env['pre.stock.landed.cost'].browse(cost_id)
                product = self.env['product.product'].browse(product_id)
                if cost_id:
                    pvp_usd = product.list_price / cost_id.rate
            else:
                pvp_usd = vals.get('price_unit') or 0.0

        return pvp_usd

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list['pvp_usd'] = self.get_lst_price_from_product(vals_list)
        else:
            for vals in vals_list:
                vals['pvp_usd'] = self.get_lst_price_from_product(vals)
        return super().create(vals_list)
