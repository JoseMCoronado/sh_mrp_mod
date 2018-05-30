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
    hide_complete = fields.Boolean('Hide Complete',compute="_hide_complete",store=False,readonly=True)
    client_order_ref = fields.Char(string="Customer PO",related="order_id.client_order_ref")

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

    @api.multi
    def print_sale_workorder(self):
        for wo in self:
            active_id = wo.id
            datas = {'ids' : [active_id]}
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'sh_mrp_mod.report_workorder',
                'datas': datas,
            }

    @api.multi
    def complete_workorder(self):
        for wo in self:
            if any(m.state not in ['done','cancel'] for m in wo.manufacturing_ids):
                for m in wo.manufacturing_ids:
                    for w in m.workorder_ids:
                        if w.state not in ['done','cancel']:
                            w.record_production()
                    if m.state not in ['done','cancel']:
                        m.state = 'done'
                        m.button_mark_done()
            for p in wo.order_id.picking_ids.filtered(lambda x:x.state not in ['cancel','draft','done']):
                p.action_assign()
                for operation in p.pack_operation_ids:
                    operation.qty_done = operation.product_qty
                p.do_new_transfer()
            return True

    @api.multi
    def _hide_complete(self):
        for wo in self:
            if any(m.state not in ['done','cancel'] for m in wo.manufacturing_ids):
                wo.hide_complete = False
            else:
                wo.hide_complete = True
