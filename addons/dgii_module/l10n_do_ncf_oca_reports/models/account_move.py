# Part of Domincana Premium.
# See LICENSE file for full copyright and licensing details.

import json

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime as dt


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _get_invoice_payment_widget(self):
        
        j = self.invoice_payments_widget
        return j["content"] if j else []

    def _compute_invoice_payment_date(self):
        for inv in self:
            if inv.payment_state not in ["reversed", "invoicing_legacy"] and inv.amount_residual == 0:
                dates = [str(payment["date"]) for payment in inv._get_invoice_payment_widget()]
                
                if dates:
                    max_date = max(dates)
 
                    invoice_date = inv.invoice_date
                    inv.payment_date = max_date if max_date >= str(invoice_date) else invoice_date
            else:
                inv.payment_date = False

    @api.depends('line_ids.tax_ids')
    def _check_isr_tax(self):
        """Restrict one ISR tax per invoice"""
        for inv in self:
            line = [
                tax_line.purchase_tax_type
                for tax_line in inv._get_tax_line_ids()
                if tax_line.purchase_tax_type in ['isr', 'ritbis']
            ]
            if len(line) != len(set(line)):
                raise ValidationError(_('An invoice cannot have multiple'
                                        'withholding taxes.'))

    def _convert_to_local_currency(self, amount):
        sign = -1 if self.move_type in ['in_refund', 'out_refund'] else 1
        amount = self.currency_id._convert(
            amount, self.company_id.currency_id, self.company_id, self.date or fields.Date.context_today(self)
        )
        return amount * sign

    def _get_tax_line_ids(self):
        return self.line_ids.tax_ids
        
    @api.depends("invoice_line_ids", "invoice_line_ids.product_id", "state")
    def _compute_amount_fields(self):
        """Compute Purchase amount by product type"""
        for inv in self:
            if inv.move_type in ["in_invoice", "in_refund"] and inv.state != "draft":
                service_amount = 0
                good_amount = 0

                for line in inv.invoice_line_ids:

                    # Monto calculado en bienes
                    if line.product_id.type in ["product", "consu"]:
                        good_amount += line.price_subtotal

                    # Si la linea no tiene un producto
                    elif not line.product_id:
                        service_amount += line.price_subtotal
                        continue

                    # Monto calculado en servicio
                    else:
                        service_amount += line.price_subtotal

                inv.service_total_amount = inv._convert_to_local_currency(service_amount)
                inv.good_total_amount = inv._convert_to_local_currency(good_amount)

    @api.depends('payment_state')
    def _compute_isr_withholding_type(self):
        """Compute ISR Withholding Type

        Keyword / Values:
        01 -- Alquileres
        02 -- Honorarios por Servicios
        03 -- Otras Rentas
        04 -- Rentas Presuntas
        05 -- Intereses Pagados a Personas Jurídicas
        06 -- Intereses Pagados a Personas Físicas
        07 -- Retención por Proveedores del Estado
        08 -- Juegos Telefónicos
        """
        for inv in self:
            if (
                inv.payment_state not in ["reversed", "invoicing_legacy"]
                and inv.amount_residual == 0
            ):  

                isr = [tax_line.tax_line_id for tax_line in inv.line_ids if tax_line.tax_line_id.purchase_tax_type == "isr"]

                if isr:
                    inv.isr_withholding_type = isr.pop(0).isr_retention_type

   
    def _get_payment_string(self):
        """Compute Vendor Bills payment method string

        Keyword / Values:
        cash        -- Efectivo
        bank        -- Cheques / Transferencias / Depósitos
        card        -- Tarjeta Crédito / Débito
        credit      -- Compra a Crédito
        swap        -- Permuta
        credit_note -- Notas de Crédito
        mixed       -- Mixto
        """
        payments = []
        p_string = ""

        for payment in self._get_invoice_payment_widget():
            payment_id = self.env["account.payment"].browse(payment.get("account_payment_id"))
            move_id = False
            if payment_id:
                if payment_id.journal_id.type in ["cash", "bank"]:
                    p_string = payment_id.journal_id.l10n_do_payment_form

            if not payment_id:
                move_id = self.env["account.move"].browse(payment.get("move_id"))
                if move_id:
                    p_string = "swap"

            # If invoice is paid, but the payment doesn't come from
            # a journal, assume it is a credit note
            payment = p_string if payment_id or move_id else "credit_note"
            payments.append(payment)

        methods = {p for p in payments}
        if len(methods) == 1:
            return list(methods)[0]
        elif len(methods) > 1:
            return "mixed"

    @api.depends("payment_state")
    def _compute_in_invoice_payment_form(self):
        for inv in self:
            if (
                inv.move_type == "in_invoice"
                and inv.payment_state not in ["reversed", "invoicing_legacy"]
                and inv.amount_residual == 0
            ):

                payment_dict = {
                    "cash": "01",
                    "bank": "02",
                    "card": "03",
                    "credit": "04",
                    "swap": "05",
                    "credit_note": "06",
                    "mixed": "07",
                }

                inv.payment_form = payment_dict.get(inv._get_payment_string())


            elif (
                inv.payment_state not in ["reversed", "invoicing_legacy"]
                and inv.amount_residual != 0
                and inv.payment_state != "not_paid"
            ):
                inv.payment_form = "07"

            else:
                inv.payment_form = "04"

    @api.depends("line_ids.tax_ids", "line_ids.tax_base_amount", "state", "invoice_line_ids")
    def _compute_invoiced_itbis(self):
        """Compute invoice invoiced_itbis taking into account the currency"""
        for inv in self:
            amount = 0
            sign = -1 if inv.move_type in ('out_refund', 'in_refund') else 1
            itbis_taxes = ["ITBIS", "ITBIS 18%"]

            tax_line_id_filter = (lambda aml, tax: True)

            for line in inv.line_ids:
                if (
                    line.tax_line_id 
                    and tax_line_id_filter(line, line.tax_line_id) 
                    and line.tax_line_id.tax_group_id.name in itbis_taxes
                    and line.tax_line_id.purchase_tax_type != "ritbis" 
                ):
                        amount += line.amount_currency

                inv.invoiced_itbis = abs(inv._convert_to_local_currency(amount)) * sign

    def _get_payment_move_iterator(self, inv, witheld_type):
        
        
        if inv.move_type == "out_invoice":
           return [
                move_line.debit
                for move_line in inv.line_ids
                if move_line.account_id.account_fiscal_type in witheld_type
            ]
        else:
            return [
                move_line.credit
                for move_line in inv.line_ids
                if move_line.account_id.account_fiscal_type in witheld_type
            ]

    @api.depends("payment_state")
    def _compute_withheld_taxes(self):
        for inv in self:

            sign = -1 if inv.is_inbound() else 1
            tax_line_id_filter = (lambda aml, tax: True)

            if (
                inv.payment_state not in ["reversed", "invoicing_legacy"]
                and inv.amount_residual == 0
            ):

                inv.withholded_itbis = 0
                inv.income_withholding = 0
                witheld_itbis_types = ["A34", "A36"]
                witheld_isr_types = ["ISR",  "A38"]

                if inv.move_type == "in_invoice":
                    ritbis_amount = 0
                    isr_amount = 0
                    for line in inv.line_ids:

                        # Monto ITBIS Retenido por impuesto
                        if (
                            line.tax_line_id 
                            and tax_line_id_filter(line, line.tax_line_id) 
                            and line.tax_line_id.purchase_tax_type == "ritbis" 
                        ):

                                ritbis_amount += line.amount_currency
                        inv.withholded_itbis = inv._convert_to_local_currency(ritbis_amount) * -1

                        
                        # Monto Retención Renta por impuesto
                        if (
                            line.tax_line_id 
                            and tax_line_id_filter(line, line.tax_line_id) 
                            and line.tax_line_id.purchase_tax_type == "isr" 
                        ):

                                isr_amount += line.amount_currency
                        inv.income_withholding = inv._convert_to_local_currency(isr_amount) * -1


                if inv.move_type == "out_invoice":
                    
                    
                    # ITBIS Retenido por Terceros
                    inv.third_withheld_itbis += sum(
                        self._get_payment_move_iterator(inv, witheld_itbis_types)
                    )

                    # Retención de Renta pr Terceros
                    inv.third_income_withholding += sum(
                        self._get_payment_move_iterator(inv, witheld_isr_types)
                    )
                elif inv.move_type == "in_invoice":
                    # ITBIS Retenido a Terceros
                    inv.withholded_itbis += sum(
                        self._get_payment_move_iterator(inv, witheld_itbis_types)
                    )

                    # Retención de Renta a Terceros
                    inv.income_withholding += sum(
                        self._get_payment_move_iterator(inv, witheld_isr_types)
                    )

    @api.depends("invoiced_itbis", "cost_itbis", "state")
    def _compute_advance_itbis(self):
        for inv in self:
            if inv.state != "draft":
                inv.advance_itbis = inv.invoiced_itbis - inv.cost_itbis

    @api.depends("l10n_latam_document_type_id.l10n_do_ncf_type")
    def _compute_is_exterior(self):
        for inv in self:
            inv.is_exterior = True if inv.l10n_latam_document_type_id.l10n_do_ncf_type in ("exterior", "e-exterior") else False

    @api.onchange("service_type")
    def onchange_service_type(self):
        self.service_type_detail = False
        return {"domain": {"service_type_detail": [("parent_code", "=", self.service_type)]}}

    @api.onchange("journal_id")
    def ext_onchange_journal_id(self):
        self.service_type = False
        self.service_type_detail = False

    # ISR Percibido       --> Este campo se va con 12 espacios en 0 para el 606
    # ITBIS Percibido     --> Este campo se va con 12 espacios en 0 para el 606
    payment_date = fields.Date(compute="_compute_taxes_fields", store=True)
    service_total_amount = fields.Monetary(
        compute="_compute_amount_fields", store=True, currency_field="company_currency_id"
    )
    good_total_amount = fields.Monetary(
        compute="_compute_amount_fields", store=True, currency_field="company_currency_id"
    )
    invoiced_itbis = fields.Monetary(
        compute="_compute_invoiced_itbis", store=True, currency_field="company_currency_id"
    )
    withholded_itbis = fields.Monetary(
        compute="_compute_withheld_taxes", store=True, currency_field="company_currency_id"
    )
    proportionality_tax = fields.Monetary(
        compute="_compute_taxes_fields", store=True, currency_field="company_currency_id"
    )
    cost_itbis = fields.Monetary(compute="_compute_taxes_fields", store=True, currency_field="company_currency_id")
    advance_itbis = fields.Monetary(compute="_compute_advance_itbis", store=True, currency_field="company_currency_id")
    isr_withholding_type = fields.Char(compute="_compute_isr_withholding_type", store=True, size=2)
    income_withholding = fields.Monetary(
        compute="_compute_withheld_taxes", store=True, currency_field="company_currency_id"
    )
    selective_tax = fields.Monetary(compute="_compute_taxes_fields", store=True, currency_field="company_currency_id")
    other_taxes = fields.Monetary(compute="_compute_taxes_fields", store=True, currency_field="company_currency_id")
    legal_tip = fields.Monetary(compute="_compute_taxes_fields", store=True, currency_field="company_currency_id")
    payment_form = fields.Selection(
        [
            ("01", "Cash"),
            ("02", "Check / Transfer / Deposit"),
            ("03", "Credit Card / Debit Card"),
            ("04", "Credit"),
            ("05", "Swap"),
            ("06", "Credit Note"),
            ("07", "Mixed"),
        ],
        compute="_compute_in_invoice_payment_form",
        store=True,
    )
    third_withheld_itbis = fields.Monetary(
        compute="_compute_withheld_taxes", store=True, currency_field="company_currency_id"
    )
    third_income_withholding = fields.Monetary(
        compute="_compute_withheld_taxes", store=True, currency_field="company_currency_id"
    )
    is_exterior = fields.Boolean(compute="_compute_is_exterior", store=True)
    service_type = fields.Selection(
        [
            ("01", "Gastos de Personal"),
            ("02", "Gastos por Trabajos, Suministros y Servicios"),
            ("03", "Arrendamientos"),
            ("04", "Gastos de Activos Fijos"),
            ("05", "Gastos de Representación"),
            ("06", "Gastos Financieros"),
            ("07", "Gastos de Seguros"),
            ("08", "Gastos por Regalías y otros Intangibles"),
        ]
    )
    service_type_detail = fields.Many2one("invoice.service.type.detail")
    fiscal_status = fields.Selection(
        [("normal", "Partial"), ("done", "Reported"), ("blocked", "Not Sent")],
        copy=False,
        help="* The 'Grey' status means ...\n"
        "* The 'Green' status means ...\n"
        "* The 'Red' status means ...\n"
        "* The blank status means that the invoice have"
        "not been included in a report.",
    )

    @api.model
    def norma_recompute(self):
        """
        This method add all compute fields into []env
        add_todo and then recompute
        all compute fields in case dgii config change and need to recompute.
        :return:
        """
        active_ids = self._context.get("active_ids")
        invoice_ids = self.browse(active_ids)
        for k, v in self.fields_get().items():
            if v.get("store") and v.get("depends"):
                self.env.add_todo(self._fields[k], invoice_ids)

        self.recompute()
    

    @api.depends("line_ids.tax_ids", "payment_state","state")
    def _compute_taxes_fields(self):
        """Compute invoice common taxes fields"""


        for inv in self:

        # tax_line_id_filter = (lambda aml, tax: True)

        # for line in self.line_ids:
        #     if line.tax_line_id and tax_line_id_filter(line, line.tax_line_id):
            sign = -1 if inv.is_inbound() else 1

            tax_line_id_filter = (lambda aml, tax: True)

            if inv.state != "draft":
                isc_amount = 0
                other_taxes = 0
                legal_tip = 0
                for line in inv.line_ids:

                    # Monto Impuesto Selectivo al Consumo
                    if (
                        line.tax_line_id 
                        and tax_line_id_filter(line, line.tax_line_id) 
                        and line.tax_line_id.tax_group_id.name == "ISC" 
                    ):
                            isc_amount += line.amount_currency

                    inv.selective_tax = inv._convert_to_local_currency(isc_amount) * sign


                    # Monto Otros Impuestos/Tasas
                    if (
                        line.tax_line_id 
                        and tax_line_id_filter(line, line.tax_line_id) 
                        and line.tax_line_id.tax_group_id.name == "Otros Impuestos"
                    ):
                            other_taxes += line.amount_currency

                    inv.other_taxes = inv._convert_to_local_currency(other_taxes) * sign

                    # Monto Propina Legal
                    if (
                        line.tax_line_id 
                        and tax_line_id_filter(line, line.tax_line_id) 
                        and line.tax_line_id.tax_group_id.name == "Propina"
                    ):
                            legal_tip += line.amount_currency

                    inv.legal_tip = inv._convert_to_local_currency(legal_tip) * sign
                # Monto Propina Legal

                # ITBIS sujeto a proporcionalidad
                inv.proportionality_tax = inv._convert_to_local_currency(
                    sum(
                        inv.line_ids.filtered(lambda line: line.account_id.account_fiscal_type in ["A29", "A30"]).mapped(
                            "amount_currency"
                        )
                    ))

                # ITBIS llevado al Costo
                inv.cost_itbis = inv._convert_to_local_currency(
                    sum(
                        inv.line_ids.filtered(lambda line: line.account_id.account_fiscal_type == "A51").mapped(
                            "amount_currency"
                        )
                    ))


                if inv.move_type == "out_invoice" and any([inv.third_withheld_itbis, inv.third_income_withholding]):
                    # Fecha Pago
                    inv._compute_invoice_payment_date()

                if inv.move_type == "in_invoice" and any([inv.withholded_itbis, inv.income_withholding]):
                    # Fecha Pago
                    inv._compute_invoice_payment_date()


