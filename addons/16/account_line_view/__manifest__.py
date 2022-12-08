# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': "Account Invoice Line",
    "description": """ccount Invoice/Bill
                    Lines Tree,Form,Kanban,Pivot,Graph,Calendar Views""",
    "summary": "Account Invoice/Bill Lines Tree,Form,Kanban,Pivot,Graph,Calendar Views",
    "category": "Accounting",
    "version": "16.0.1.0.0",
    'author': "Astratech",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['account'],
    'data': [
        'views/invoice_line_view.xml',
        'views/bill_line_view.xml',
        'views/credit_note_line_view.xml',
        'views/refund_line_view.xml',
        'views/account_move_line_view.xml'
    ],
    'images': [
        'static/description/banner.png', ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
