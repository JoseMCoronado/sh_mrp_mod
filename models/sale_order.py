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
    workorder_count = fields.Float(string='Workorders',
    compute='_get_wo_count', readonly=True,
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
    def _get_wo_count(self):
        for order in self:
            mfg_orders = order.env['mrp.production'].search([('procurement_group_id.name','=',order.name)])
            total_count = 0
            for mfg in mfg_orders:
                for work_order in mfg.workorder_ids:
                    total_count += 1
            order.workorder_count = total_count

    @api.multi
    def action_view_work_orders(self):
        action_data = self.env.ref('sh_mrp_mod.action_sale_workorder_form').read()[0]
        action_data['res_id'] = self.env['sale.workorder'].search([('order_id','=',self.id)],limit=1).id
        return action_data

    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        for order in self:
            mfg_orders = order.env['mrp.production'].search([('procurement_group_id.name','=',order.name)])
            if mfg_orders:
                sale_workorder = order.env['sale.workorder'].create({'order_id':order.id})
            for mfg in mfg_orders:
                mfg.button_plan()
                for work_order in mfg.workorder_ids:
                    work_order.sale_workorder_id = sale_workorder
        return True
