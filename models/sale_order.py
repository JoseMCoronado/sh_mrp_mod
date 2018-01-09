# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    workorder_count = fields.Integer(string='Workorders',compute='_get_wo_count',readonly=True,store=False)
    workorder_ids = fields.One2many('sale.workorder', 'order_id', string='Workorders')
    show_release = fields.Char(string='Show Release (Technical)',compute='_show_release', readonly=True,store=False)
    requested_date = fields.Datetime('Requested Date', readonly=False,copy=False,
                                     help="Date by which the customer has requested the items to be "
                                          "delivered.\n"
                                          "When this Order gets confirmed, the Delivery Order's "
                                          "expected date will be computed based on this date and the "
                                          "Company's Security Delay.\n"
                                          "Leave this field empty if you want the Delivery Order to be "
                                          "processed as soon as possible. In that case the expected "
                                          "date will be computed using the default method: based on "
                                          "the Product Lead Times and the Company's Security Delay.")
    commitment_date = fields.Datetime(readonly=False, string='Commitment Date', store=True,
                                      compute='_compute_commitment_date', help="Date by which the products are sure to be delivered. This is "
                                           "a date that you can promise to the customer, based on the "
                                           "Product Lead Times.")
    @api.multi
    def _get_wo_count(self):
        for order in self:
            order.workorder_count = len(order.workorder_ids)

    @api.multi
    def action_view_work_orders(self):
        action = self.env.ref('sh_mrp_mod.action_sale_workorder_tree')
        result = action.read()[0]
        result['context'] = {}
        all_workorder_ids = sum([order.workorder_ids.ids for order in self], [])
        if len(all_workorder_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, all_workorder_ids)) + "])]"
        elif len(all_workorder_ids) == 1:
            res = self.env.ref('sh_mrp_mod.view_sale_workorder_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = all_workorder_ids and all_workorder_ids[0] or False
        return result

    @api.multi
    def _show_release(self):
        for order in self:
            order.show_release = False
            for l in order.order_line:
                if l.product_id.product_tmpl_id.bom_ids:
                    manufactured_qty = sum(m.product_qty for m in l.manufacturing_ids.filtered(lambda r: r.state != 'cancel'))
                    if manufactured_qty < l.product_uom_qty:
                        order.show_release = True

    @api.onchange('requested_date')
    def onchange_requested_date(self):
        return False

    @api.depends('date_order', 'order_line.customer_lead')
    def _compute_commitment_date(self):
        for order in self:
            return False

    @api.multi
    def release_production(self):
        for order in self:
            create_workorder = False
            created_mfg_orders = []
            for l in order.order_line:
                if l.product_id.product_tmpl_id.bom_ids:
                    to_produce_qty = l.product_uom_qty - sum(order.env['mrp.production'].search([('sale_line_id','=',l.id)]).filtered(lambda r: r.state != 'cancel').mapped('product_qty'))
                    print to_produce_qty
                    if to_produce_qty > 0:
                        mfg_values= {
                            'product_id': l.product_id.id,
                            'product_uom_id': l.product_uom.id,
                            'bom_id': l.product_id.product_tmpl_id.bom_ids[0].id,
                            'product_qty': to_produce_qty,
                            'procurement_group_id': order.procurement_group_id.id,
                            'sale_line_id': l.id,
                        }
                        mfg_order = order.env['mrp.production'].create(mfg_values)
                        mfg_order.button_plan()
                        for wo in mfg_order.workorder_ids:
                            if wo.operation_id.initial_ops == True:
                                wo.state = 'ready'
                        create_workorder = True
                        created_mfg_orders.append(mfg_order.id)

            if create_workorder == True:
                sale_workorder_values = {
                    'order_id': order.id,
                    'manufacturing_ids': [(6, 0, created_mfg_orders)],
                    'requested_date': order.requested_date,
                    'commitment_date': order.commitment_date,
                    'partner_id': order.partner_id.id,
                    'partner_shipping_id': order.partner_shipping_id.id,
                    'user_id': order.user_id.id,
                }
                sale_workorder = order.env['sale.workorder'].create(sale_workorder_values)
                action = order.env.ref('sh_mrp_mod.action_sale_workorder_tree')
                result = action.read()[0]
                res = order.env.ref('sh_mrp_mod.view_sale_workorder_form', False)
                result['views'] = [(res and res.id or False, 'form')]
                result['res_id'] = sale_workorder.id
                return result

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    manufacturing_ids = fields.One2many('mrp.production', 'sale_line_id', string='Manufacturing Orders')

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()

        return {}
