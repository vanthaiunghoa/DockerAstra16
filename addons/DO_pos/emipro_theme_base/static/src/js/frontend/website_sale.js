odoo.define('emipro_theme_base.website_sale', function(require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    var WebsiteSale = require('website_sale.website_sale');
    var VariantMixin = require('sale.VariantMixin');
    var timer;
    var ajax = require('web.ajax');
    var OwlMixin = require('theme_clarico_vega.mixins');
    var core = require('web.core');
    var _t = core._t;

publicWidget.registry.dynamic_snippet_products_cta.include({
    start: function () {
            this.$el.popover({
                trigger: 'manual',
                animation: true,
                html: true,
                title: function () {
                    return _t("My Cart");
                },
                container: 'body',
                placement: 'auto',
                template: '<div class="popover mycart-popover te_open" role="tooltip"><div class="tooltip-arrow"></div><h3 class="popover-header"></h3><div class="te_cross"></div><div class="popover-body"></div></div>'
            });
            return this._super.apply(this, arguments);
        },
    async _onClickAddToCart(ev) {
        this._super.apply(this, arguments);
        var temp = $(ev.currentTarget).closest('.card').find('input[data-product-id]').data('product-id');
        if ($('input#notification_toast').val()) {
            await this.displayNotificationToast(temp);
        }
        else if($('input#notification_sidebar').val()){
            await this.displayCartSidebar()
        }
        else if($('input#confirmation_popup').val()){
            await this.displayConfirmationPopup(temp,1);
        }
    },
    displayNotificationToast: function(product_variant_id){
            var params = {
                'product_variant_id': product_variant_id
            }
            $('#quick_view_model_shop').modal('hide');
            $(".quick_close").on('click', function() {
                $('#quick_view_model_shop').modal('hide');
                $('#quick_view_model').modal('hide');
                $("#quick_view_model_shop .modal-body").html('');
            });
            ajax.jsonRpc('/get_toast_token_details', 'call', params).then(function (data){
                let timer1, timer2;
                $('.toast').addClass("active");
                $('.toast').addClass("show");
                $('.progress').addClass("active");
                $('.product_name_toast').text(data.name);
                $('img.toast_product_img').attr('src', data.image)
                timer1 = setTimeout(() => {
                $('.toast').removeClass("active");
                }, 5000);
                timer2 = setTimeout(() => {
                $('.progress').removeClass("active");
                $('.toast').removeClass("show");
                }, 5300);
                $(".toast .close_toast").on('click', function() {
                    $('.toast').removeClass("show");
                    $('.toast').removeClass("active");
                });
            });
        },
    displayCartSidebar: function () {
        if ($(window).width() > 991) {
            let self = this;
            var timeout;
            self.hovered = true;
            clearTimeout(timeout);
            var path = window.location.pathname
            timeout = setTimeout(function () {
                if (!self.hovered || $('.mycart-popover:visible').length) {
                    return;
                }
                self._popoverRPC = $.get("/shop/cart", {
                    type: 'popover',
                }).then(function (data) {
                    var cartPopup = new publicWidget.registry.cart_popup();
                    const popover = Popover.getInstance(self.$el[0]);
                    popover._config.content = data;
                    popover.setContent(popover.getTipElement());
                    self.$el.popover("show");

                    $(".mycart-popover .popover-body").html(data);
                    if (path == '/shop/payment')
                    {
                        $(".mycart-popover .popover-body").find('.te_prod_rm_info').remove()
                        $(".mycart-popover .popover-body").find('.line_qty').removeClass('d-none')
                        $(".mycart-popover .popover-body").find('.js_delete_product').remove()
                    }
                    $('.popover').on('mouseleave', function () {
                        self.$el.trigger('mouseleave');
                    });
                    $('.mycart-popover .js_add_cart_json').off('click').on('click',function(ev) {
                        ev.preventDefault();
                        cartPopup._onUpdateQuantity(ev)
                    });
                    $(".mycart-popover .js_quantity[data-product-id]").off('change').on('change',function(ev) {
                        ev.preventDefault();
                        cartPopup._onChangeQuantity(ev)
                    });
                    $(".mycart-popover .js_delete_product").off('click').on('click',function(ev) {
                        ev.preventDefault();
                        cartPopup._onClickRemoveItem(ev)
                    });
                    $(".te_clear_cart_popover").on('click', function(ev) {
                        ajax.jsonRpc('/shop/clear_cart', 'call', {}).then(function (data) {
                            $(".my_cart_quantity").html('0');
                        });
                    });
                    $(document).on('click', '.te_cross', function(ev) {
                        $(".mycart-popover").removeClass("te_open");
                        $("#wrapwrap").removeClass("te_overlay");
                        $('.mycart-popover').remove()
                    });
                    self.cartQty = +$(data).find('.o_wsale_cart_quantity').text();
                    sessionStorage.setItem('website_sale_cart_quantity', self.cartQty);
                });
            }, 300);
        }
        },
    displayConfirmationPopup: function(product_variant_id,addQty){
        var params = {
            'product_variant_id': product_variant_id
        }
        $('.toast_confirmation').html();
        ajax.jsonRpc('/get_confirmation_popup_details', 'call', params).then(function (data){
            $('.toast_confirmation').html(data);
            $('.optional_div').each(function(index){
                var responsive = { 0: {items: 2}, 576: {items: 3} };
                OwlMixin.initOwlCarousel('.optional_div', 20, responsive, true, 1, false, true, true, true, true, false, true, false);
            });
            $('.item_count').html(parseInt($('.total_item').text()) + addQty);
            $("#quick_view_model .modal-body").append($('.toast_confirmation'));
            $('#quick_view_model').modal('show');
            $('.quick_view_modal').css({'width':'max-content', 'margin': 'auto'});
        });
    },
});
    publicWidget.registry.WebsiteSale.include({
        start: function () {
            this.$el.popover({
                trigger: 'manual',
                animation: true,
                html: true,
                title: function () {
                    return _t("My Cart");
                },
                container: 'body',
                placement: 'auto',
                template: '<div class="popover mycart-popover te_open" role="tooltip"><div class="tooltip-arrow"></div><h3 class="popover-header"></h3><div class="te_cross"></div><div class="popover-body"></div></div>'
            });
            return this._super.apply(this, arguments);
        },
        _onChangeCombination: function(ev, $parent, combination) {
            this._super.apply(this, arguments);
            $('.td-product_name .product-name');
            $(".js_sku_div").html('N/A');
            if (combination.sku_details) {
                $(".js_sku_div").html(combination.sku_details);
            }
            $(".js_product .te_discount, .js_product .te_discount_before").addClass('d-none');
            $(".js_product .te_discount, .js_product .te_percentage").hide()
            if (combination.has_discounted_price) {
                $(".js_product .te_discount, .js_product .te_discount_before").removeClass('d-none');
                var difference = combination.list_price - combination.price;
                var discount = difference * 100 / combination.list_price;
                if (discount > 0) {
                    $(".js_product .te_discount_before .oe_currency_value").html(difference.toFixed(2));
                    $(".js_product .te_discount .te_percentage .percent_val").html(discount.toFixed(2));
                    $(".js_product .te_discount, .js_product .te_percentage").show()
                }
            }
            if($('#id_lazyload').length) {
                $('img.lazyload').lazyload();
            }
        },
        _onChangeAttribute: function(ev) {
            $('.cus_theme_loader_layout').removeClass('d-none');
            this._super.apply(this, arguments);
        },
        _submitForm: function () {
            this._super.apply(this, arguments);
            $('#quick_view_model_shop').modal('hide');
            if(this.isBuyNow != true){
                if ($('input#notification_toast').val()) {
                    this.displayNotificationToast(this.rootProduct.product_id);
                }
                else if($('input#notification_sidebar').val()){
                    this.displayCartSidebar()
                }
                else if($('input#confirmation_popup').val()){
                    this.displayConfirmationPopup(this.rootProduct.product_id, this.rootProduct.add_qty);
                }
            }
        },
        _onModalSubmit: function (goToShop) {
            this._super.apply(this, arguments);
            const products = [];
            this.$('.js_product.in_cart').each((i, el) => {
                products.push({
                    'item_id': el.getElementsByClassName('product_id')[0].value,
                    'quantity':el.getElementsByClassName('js_quantity')[0].value,
                });
            });
            if ($('input#notification_toast').val()) {
                this.displayNotificationToast(products[0].item_id);
            }
            else if($('input#notification_sidebar').val()){
                this.displayCartSidebar()
            }
            else if($('input#confirmation_popup').val()){
                this.displayConfirmationPopup(products[0].item_id, products[0].quantity);
            }
        },
        displayNotificationToast: function(product_variant_id){
            var params = {
                'product_variant_id': product_variant_id
            }
            $('#quick_view_model_shop').modal('hide');
            $(".quick_close").on('click', function() {
                $('#quick_view_model_shop').modal('hide');
                $('#quick_view_model').modal('hide');
                $("#quick_view_model_shop .modal-body").html('');
            });
            ajax.jsonRpc('/get_toast_token_details', 'call', params).then(function (data){
                let timer1, timer2;
                $('.toast').addClass("active");
                $('.toast').addClass("show");
                $('.progress').addClass("active");
                $('.product_name_toast').text(data.name);
                $('img.toast_product_img').attr('src', data.image)
                timer1 = setTimeout(() => {
                $('.toast').removeClass("active");
                }, 5000);
                timer2 = setTimeout(() => {
                $('.progress').removeClass("active");
                $('.toast').removeClass("show");
                }, 5300);
                $(".toast .close_toast").on('click', function() {
                    $('.toast').removeClass("show");
                    $('.toast').removeClass("active");
                });
            });
        },
        displayCartSidebar: function () {
        if ($(window).width() > 991) {
            let self = this;
            var timeout;
            self.hovered = true;
            clearTimeout(timeout);
            var path = window.location.pathname
            timeout = setTimeout(function () {
                if (!self.hovered || $('.mycart-popover:visible').length) {
                    return;
                }
                self._popoverRPC = $.get("/shop/cart", {
                    type: 'popover',
                }).then(function (data) {
                    var cartPopup = new publicWidget.registry.cart_popup();
                    const popover = Popover.getInstance(self.$el[0]);
                    popover._config.content = data;
                    popover.setContent(popover.getTipElement());
                    self.$el.popover("show");

                    $(".mycart-popover .popover-body").html(data);
                    if (path == '/shop/payment')
                    {
                        $(".mycart-popover .popover-body").find('.te_prod_rm_info').remove()
                        $(".mycart-popover .popover-body").find('.line_qty').removeClass('d-none')
                        $(".mycart-popover .popover-body").find('.js_delete_product').remove()
                    }
                    $('.popover').on('mouseleave', function () {
                        self.$el.trigger('mouseleave');
                    });
                    $('.mycart-popover .js_add_cart_json').off('click').on('click',function(ev) {
                        ev.preventDefault();
                        cartPopup._onUpdateQuantity(ev)
                    });
                    $(".mycart-popover .js_quantity[data-product-id]").off('change').on('change',function(ev) {
                        ev.preventDefault();
                        cartPopup._onChangeQuantity(ev)
                    });
                    $(".mycart-popover .js_delete_product").off('click').on('click',function(ev) {
                        ev.preventDefault();
                        cartPopup._onClickRemoveItem(ev)
                    });
                    $(".te_clear_cart_popover").on('click', function(ev) {
                        ajax.jsonRpc('/shop/clear_cart', 'call', {}).then(function (data) {
                            $(".my_cart_quantity").html('0');
                        });
                    });
                    $(document).on('click', '.te_cross', function(ev) {
                        $(".mycart-popover").removeClass("te_open");
                        $("#wrapwrap").removeClass("te_overlay");
                        $('.mycart-popover').remove()
                    });
                    self.cartQty = +$(data).find('.o_wsale_cart_quantity').text();
                    sessionStorage.setItem('website_sale_cart_quantity', self.cartQty);
                });
            }, 300);
        }
        },
        displayConfirmationPopup: function(product_variant_id,addQty){
            var params = {
                'product_variant_id': product_variant_id
            }
            $('.toast_confirmation').html();
            ajax.jsonRpc('/get_confirmation_popup_details', 'call', params).then(function (data){
                $('.toast_confirmation').html(data);
                $('.optional_div').each(function(index){
                    var responsive = { 0: {items: 2}, 576: {items: 3} };
                    OwlMixin.initOwlCarousel('.optional_div', 20, responsive, true, 1, false, true, true, true, true, false, true, false);
                });
                $('.item_count').html(parseInt($('.total_item').text()) + addQty);
                $("#quick_view_model .modal-body").append($('.toast_confirmation'));
                $('#quick_view_model').modal('show');
                $('.quick_view_modal').css({'width':'max-content', 'margin': 'auto'});
            });
        },
    });
});
