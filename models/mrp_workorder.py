# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    requested_date = fields.Datetime(string='Requested Date',
    readonly=True, store=False, index=True, copy=False, compute='_get_dates',)
    commitment_date = fields.Datetime(string='Commitment Date',
    readonly=True, store=False, index=True, copy=False, compute='_get_dates',)
    product_image = fields.Binary(string='Product Image',
    readonly=True, related='product_id.product_tmpl_id.image', store=False)
    line_desc = fields.Char(string='Line Description',
    compute='_get_line_info', readonly=True,store=False)
    line_qty = fields.Char(string='Line Qty',
    compute='_get_line_info', readonly=True,store=False)

    @api.multi
    def _get_dates(self):
        for work in self:
            work.requested_date = work.production_id.requested_date
            work.commitment_date = work.production_id.requested_date

    @api.multi
    def button_finish(self):
        super(MrpWorkorder, self).button_finish()
        if all(wo.state == 'done' for wo in self.production_id.workorder_ids):
            self.production_id.button_mark_done()

    @api.multi
    def _get_line_info(self):
        def get_parent_move(move):
            if move.move_dest_id:
                return get_parent_move(move.move_dest_id)
            return move
        for order in self:
            move = get_parent_move(order.production_id.move_finished_ids[0])
            sale_line = move.procurement_id.sale_line_id
            order.line_desc = sale_line.name
            order.line_qty = sale_line.product_uom_qty
