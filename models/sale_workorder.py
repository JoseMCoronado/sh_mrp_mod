# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError

class SaleWorkorder(models.Model):
    _name = "sale.workorder"
    _description = 'Sale Work Order'
    _order = 'id desc'

    name = fields.Char(string='Work Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    manufacturing_ids = fields.One2many('mrp.production', 'sale_workorder_id', string='Manufacturing Lines')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    requested_date = fields.Datetime(string='Requested Date',
    readonly=False, store=True, index=True, copy=False)
    commitment_date = fields.Datetime(string='Commitment Date',
    readonly=False, store=True, index=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address')
    user_id = fields.Many2one('res.users', string='Salesperson')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.workorder.sequence') or _('New')
        result = super(SaleWorkorder, self).create(vals)
        return result

    @api.multi
    def delete_workorder(self):
        for wo in self:
            for mo in wo.manufacturing_ids:
                mo.action_cancel()
            wo.unlink()
