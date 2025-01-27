# -*- encoding: UTF-8 -*-
##############################################################################
#	
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': 'Seller on Payments',
    'summary': """Campo vendedor en form pagos de clientes""",
    'version': '15.0.1.0.',
    'description': """Campo vendedor en form pagos de clientes y vista de lista""",
    'author': 'Astratech',
    'maintainer': '',
    'website': 'https://www.solucionesabacus.com',
    'category': 'account',
    'depends': ['account', 'payment', 'base'],
    'license': 'AGPL-3',
    'data': [
            'views/account_payment_view_seller.xml',
             ],
    'demo': [],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,

}
