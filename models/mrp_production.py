# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_workorder_id = fields.Many2one('sale.workorder', string='Sale Workorder')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Workorder')
    sale_order_line_desc = fields.Text('Sale Line Desc', related='sale_line_id.name',readonly=True)
    workorder_desc = fields.Text('Description',compute='_compute_workorder_desc',readonly=True,store=False)
    stage = fields.Text('stage',compute='_compute_stage',readonly=True,store=False)
    product_kit_id = fields.Many2one('product.product', string='Kit Product')

    @api.multi
    def _compute_workorder_desc(self):
        for mrp in self:
            if not mrp.product_kit_id:
                mrp.workorder_desc = mrp.sale_order_line_desc
            else:
                parsed_desc = mrp.product_id.name
                second_package = "---" + '\n'
                for values in mrp.sale_line_id.attribute_id.attribute_values:
                    second_package += '    ' + str(values.categ_id.name) + ': ' + str(values.value) + '\n'
                new_desc = parsed_desc + second_package
                mrp.workorder_desc = new_desc

    @api.multi
    def _compute_stage(self):
        for mrp in self:
            active_wo_ids = mrp.workorder_ids.filtered(lambda r: r.state in ['ready','rework','hold'])
            if len(active_wo_ids)>0:
                text = ""
                for wo in active_wo_ids:
                    text += wo.workcenter_id.name + " ["+ wo.state +"] " + "\n"
                mrp.stage = text
            else:
                mrp.stage = "Finished"

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

    @api.multi
    def remove_from_workorder(self):
        for mrp in self:
            for wo in mrp.workorder_ids:
                wo.action_cancel()
            mrp.sale_workorder_id = False
            mrp.action_cancel()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
