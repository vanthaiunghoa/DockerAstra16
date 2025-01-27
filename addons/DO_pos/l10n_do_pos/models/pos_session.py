# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()
        result['search_params']['fields'].extend(['company_address', 'l10n_do_ncf_exp_date'])
        return result

    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].extend(['l10n_do_dgii_tax_payer_type'])
        return result

    def _confirm_orders(self):
        for session in self:
            company_id = session.config_id.journal_id.company_id.id
            orders = session.order_ids.filtered(lambda order: order.state ==
                                                'paid')
            journal_id = self.env['ir.config_parameter'].sudo().get_param(
                'pos.closing.journal_id_%s' % company_id,
                default=session.config_id.journal_id.id)
            if not journal_id:
                raise UserError(
                    _("You have to set a Sale Journal for the POS:%s") %
                    (session.config_id.name,)
                )

            move = self.env['pos.order'].with_context(
                force_company=company_id)._create_account_move(
                    session.start_at, session.name, int(journal_id),
                    company_id)
            orders.with_context(
                force_company=company_id)._create_account_move_line(
                    session, move)
            for order in session.order_ids.filtered(lambda o: o.state not in [
                    'done', 'invoiced', 'is_return_order'
            ]):
                if order.state not in ('paid'):
                    raise UserError(
                        _("You cannot confirm all orders of this session,"
                          " because they have not the 'paid' status.\n"
                          " {reference} is in state {state}, total amount:"
                          " {total}, paid: {paid}").format(
                              reference=order.pos_reference or order.name,
                              state=order.state,
                              total=order.amount_total,
                              paid=order.amount_paid)
                    )
                order.action_pos_order_done()
            orders = session.order_ids.filtered(lambda order: order.state in
                                                ['invoiced', 'done'])
            orders.sudo()._reconcile_payments()
