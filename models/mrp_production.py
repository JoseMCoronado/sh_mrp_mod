# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    #requested_date = fields.Datetime(string='Requested Date',
    #readonly=True, store=False, index=True, copy=False, compute='_get_dates',)
    #commitment_date = fields.Datetime(string='Commitment Date',
    #readonly=True, store=False, index=True, copy=False, compute='_get_dates',)
    sale_count = fields.Float(string='Sale Order',
    compute='_get_sale_count', readonly=True,store=False)

    @api.multi
    def _get_sale_count(self):
        def get_parent_move(move):
            if move.move_dest_id:
                return get_parent_move(move.move_dest_id)
            return move
        for order in self:
            move = get_parent_move(order.move_finished_ids[0])
            sale_order = move.procurement_id.sale_line_id.order_id
            order.sale_count = len(sale_order)

    @api.multi
    def action_view_sale_orders(self):
        def get_parent_move(move):
            if move.move_dest_id:
                return get_parent_move(move.move_dest_id)
            return move
        move = get_parent_move(self.move_finished_ids[0])
        action_data = self.env.ref('sale.action_orders').read()[0]
        action_data['domain'] = [('name','=',move.procurement_id.sale_line_id.order_id.name)]
        return action_data

    @api.multi
    def _generate_moves(self):
        for production in self:
            production._generate_finished_moves()
            factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            production._generate_raw_moves(lines)
            production._adjust_procure_method()
            production.move_raw_ids.action_cancel()
        return True

    #@api.multi
    #def _get_dates(self):
    #    def get_parent_move(move):
    #        if move.move_dest_id:
    #            return get_parent_move(move.move_dest_id)
    #        return move
    #    for production in self:
    #        move = get_parent_move(production.move_finished_ids[0])
    #        production.requested_date = move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.requested_date or False
    #        production.commitment_date = move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.commitment_date or False
