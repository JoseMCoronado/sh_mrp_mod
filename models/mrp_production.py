# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_workorder_id = fields.Many2one('sale.workorder', string='Sale Workorder')

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

    @api.multi
    def action_update_mo_qty(self):
        action_data = self.env.ref('mrp.action_change_production_qty').read()[0]
        action_data['context'] = {'default_mo_id': self.id}
        return action_data

    @api.multi
    def action_view_workorders(self):
        action_data = self.env.ref('mrp.action_mrp_workorder_production_specific').read()[0]
        return action_data
