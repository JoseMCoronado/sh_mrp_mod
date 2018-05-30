# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    has_bom = fields.Boolean(string="Has BoM",compute="_compute_has_bom",store=False)

    @api.multi
    def _compute_has_bom(self):
        for record in self:
            if record.product_id.bom_ids:
                record.has_bom = True

    @api.multi
    def action_see_bom(self):
        for record in self:
            action_data = record.env.ref('mrp.mrp_bom_form_action').read()[0]
            #action_data.update({'res_id': record.product_id.bom_ids[0].id,'view_mode':'form'})
            action_data['views'] = [(False, 'form')]
            action_data['res_id'] = record.product_id.bom_ids[0].id or False
            return action_data

    @api.multi
    def action_see_template(self):
        for record in self:
            action_data = record.env.ref('product.product_template_action').read()[0]
            #res = self.env.ref('sh_mrp_mod.view_sale_workorder_form', False)
            action_data['views'] = [(False, 'form')]
            action_data['res_id'] = record.product_id.product_tmpl_id.id or False
            return action_data
