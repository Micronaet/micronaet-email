# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)


class ResPartner(orm.Model):
    """ Model name: ResPartner
    """    
    _inherit = 'res.partner'

    # -------------------------------------------------------------------------
    # Field function:
    # -------------------------------------------------------------------------
    def _function_get_related_email(
            self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''
        res = {}
        field_id = fields.replace('address', 'id')
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = partner.__getattribute__(field_id).email or False
        return res

    def _function_set_related_email(
            self, cr, uid, partner_id, name, value, arg, context=None):
        ''' Fields function for calculate context
        current_proxy = self.browse(cr, uid, partner_id, context=context)
        contact_name = '%s [%s]' % (current_proxy.name, name.split('_')[1])
        '''
        current_proxy = self.browse(cr, uid, partner_id, context=context)
        field_id = name.replace('address', 'id')
        contact_name = '%s [%s]' % (
            current_proxy.name,
            name.split('_')[1],
            )

        try: # remove extra spaces:
            value = value.strip()
        except:
            return False
        if not value:
            return False    

        contact_id = current_proxy.__getattribute__(field_id).id
        if contact_id:
            self.write(cr, uid, contact_id, {
                'email': value,
                }, context=context)
        else:
            contact_id = self.create(cr, uid, {
                'name': contact_name,
                'email': value,
                'parent_id': partner_id,
                }, context=context)
            self.write(cr, uid, partner_id, {
                field_id: contact_id,
                }, context=context)              
        return True

    _columns = {
        # Partner linked:
        'email_quotation_id': fields.many2one(
            'res.partner', 'Partner email quotation'),
        'email_order_id': fields.many2one(
            'res.partner', 'Partner email order'),
        'email_confirmation_id': fields.many2one(
            'res.partner', 'Partner email confirmation'),
        'email_pricelist_id': fields.many2one(
            'res.partner', 'Partner email pricelist'),
        'email_picking_id': fields.many2one(
            'res.partner', 'Partner email picking'),
        'email_ddt_id': fields.many2one(
            'res.partner', 'Partner email ddt'),
        'email_invoice_id': fields.many2one(
            'res.partner', 'Partner email invoice'),
        'email_promotional_id': fields.many2one(
            'res.partner', 'Partner email promotional'),
        'email_payment_id': fields.many2one(
            'res.partner', 'Partner email payment'),

        # Related email:
        'email_quotation_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email quotation', store=False, 
            ), 
        'email_order_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email order', store=False, 
            ), 
        'email_confirmation_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email confirmation', store=False, 
            ), 
        'email_pricelist_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email pricelist', store=False, 
            ), 
        'email_picking_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email picking', store=False, 
            ), 
        'email_ddt_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email ddt', store=False, 
            ), 
        'email_invoice_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email invoice', store=False, 
            ), 
        'email_promotional_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email promotional', store=False, 
            ), 
        'email_payment_address': fields.function(
            _function_get_related_email, 
            fnct_inv=_function_set_related_email, method=True, 
            type='char', string='Email payment', store=False, 
            ), 

        # XXX To remove XXX:    
        'email_quotation': fields.char('Quotation email', size=80,
            help='Address for send quotation'),
        'email_order': fields.char('Order email', size=80,
            help='Address for send order'),
        'email_confirmation': fields.char('Order confirm', size=80,
            help='Address for send order confirmation'),
        'email_pricelist': fields.char('Pricelist email', size=80,
            help='Address for send pricelist'),
        'email_picking': fields.char('Picking email', size=80,
            help='Address for send generic picking document'),
        'email_ddt': fields.char('DDT email', size=80,
            help='Address for send DDT'),
        'email_invoice': fields.char('Invoice email', size=80,
            help='Address for send invoice'),
        'email_promotional': fields.char('Promotional email', size=80,
            help='Address for send promotional material'),
        'email_payment': fields.char('Payment email', size=80,
            help='Address for send payment request or information'),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
