# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    mfg_count = fields.Float(string='Mfg Orders',
    compute='_get_mfg_count', readonly=True,
    store=False)

    @api.multi
    def _get_mfg_count(self):
        for order in self:
            mfg_orders = len(order.env['mrp.production'].search([('procurement_group_id.name','=',order.name)]))
            order.mfg_count = mfg_orders

    @api.multi
    def action_view_mfg_orders(self):
        action_data = self.env.ref('mrp.mrp_production_action').read()[0]
        action_data['domain'] = [('procurement_group_id.name','=',self.name)]
        return action_data

    @api.multi
    def action_confirm(self):
        for order in self:
            super(SaleOrder, self).action_confirm()
            mfg_orders = order.env['mrp.production'].search([('procurement_group_id.name','=',order.name)])
            for mfg in mfg_orders:
                mfg.button_plan()
