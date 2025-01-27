# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'RFQ From Sale',
    'version': '16.0.0.0',
    'author': 'Astratech',
    'summary': 'RFQ From Sale Order',
    'description': """This module helps to create rfq from sale order screen.""",
    'category': 'Sales',
    'website': 'https://www.iwesabe.com/',
    'license': 'LGPL-3',
    'depends': ['sale','purchase'],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_views.xml',
    ],
    'qweb': [],
    'images': ['static/description/iWesabe-Apps-Rfq-From-Sale.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
