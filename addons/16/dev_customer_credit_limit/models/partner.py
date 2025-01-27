# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields

class res_partner(models.Model):
    _inherit= 'res.partner'
    
    check_credit = fields.Boolean('Check Credit',tracking=True, default=True)
    credit_limit_on_hold  = fields.Boolean('Credit limit on hold', tracking=True, default=True)
    credit_limit = fields.Float(string='Credit Limit' , tracking=True)

