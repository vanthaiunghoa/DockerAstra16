odoo.define('l10n_do_pos.PaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { isConnectionError } = require('point_of_sale.utils');

    const PosRestrictInvoice = PaymentScreen =>
        class extends PaymentScreen {
            //reimplementando
            async _finalizeValidation() {
                if ((this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) && this.env.pos.config.iface_cashdrawer) {
                    this.env.proxy.printer.open_cashbox();
                }

                this.currentOrder.initialize_validation_date();
                this.currentOrder.finalized = true;

                let syncOrderResult, hasError;

                try {
                    // 1. Save order to server.
                    syncOrderResult = await this.env.pos.push_single_order(this.currentOrder);

                    // 2. Invoice.
                    if (this.currentOrder.is_to_invoice() && this.env.pos.config.print_pdf) {
                        if (syncOrderResult.length) {
                            await this.env.legacyActionManager.do_action('account.account_invoices', {
                                additional_context: {
                                    active_ids: [syncOrderResult[0].account_move],
                                },
                            });
                        } else {
                            throw { code: 401, message: 'Backend Invoice', data: { order: this.currentOrder } };
                        }
                    }

                    // 3. Post process.
                    if (syncOrderResult.length && this.currentOrder.wait_for_push_order()) {
                        const postPushResult = await this._postPushOrderResolve(
                            this.currentOrder,
                            syncOrderResult.map((res) => res.id)
                        );
                        if (!postPushResult) {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Error: no internet connection.'),
                                body: this.env._t('Some, if not all, post-processing after syncing order failed.'),
                            });
                        }
                    }
                } catch (error) {
                    if (error.code == 700 || error.code == 701)
                        this.error = true;

                    if ('code' in error) {
                        // We started putting `code` in the rejected object for invoicing error.
                        // We can continue with that convention such that when the error has `code`,
                        // then it is an error when invoicing. Besides, _handlePushOrderError was
                        // introduce to handle invoicing error logic.
                        await this._handlePushOrderError(error);
                    } else {
                        // We don't block for connection error. But we rethrow for any other errors.
                        if (isConnectionError(error)) {
                            this.showPopup('OfflineErrorPopup', {
                                title: this.env._t('Connection Error'),
                                body: this.env._t('Order is not synced. Check your internet connection'),
                            });
                        } else {
                            throw error;
                        }
                    }
                } finally {
                    // Always show the next screen regardless of error since pos has to
                    // continue working even offline.
                    this.showScreen(this.nextScreen);
                    // Remove the order from the local storage so that when we refresh the page, the order
                    // won't be there
                    this.env.pos.db.remove_unpaid_order(this.currentOrder);

                    // Ask the user to sync the remaining unsynced orders.
                    if (!hasError && syncOrderResult && this.env.pos.db.get_orders().length) {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Remaining unsynced orders'),
                            body: this.env._t(
                                'There are unsynced orders. Do you want to sync these orders?'
                            ),
                        });
                        if (confirmed) {
                            // NOTE: Not yet sure if this should be awaited or not.
                            // If awaited, some operations like changing screen
                            // might not work.
                            this.env.pos.push_orders();
                        }
                    }
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PosRestrictInvoice);
    return PaymentScreen;
});
