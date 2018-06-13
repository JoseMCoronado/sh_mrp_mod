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

class BomStructureReport(models.AbstractModel):
    _inherit = 'report.mrp.report_mrpbomstructure'

    def get_children(self, object, level=0):
        result = []

        def _get_rec(object, level, qty=1.0, uom=False):
            for l in object:
                res = {}
                res['pname'] = l.product_id.name_get()[0][1]
                res['pcode'] = l.product_id.default_code
                res['punitcost'] = l.product_id.standard_price
                qty_per_bom = l.bom_id.product_qty
                if uom:
                    if uom != l.bom_id.product_uom_id:
                        qty = uom._compute_quantity(qty, l.bom_id.product_uom_id)
                    res['pqty'] = (l.product_qty *qty)/ qty_per_bom
                else:
                    #for the first case, the ponderation is right
                    res['pqty'] = (l.product_qty *qty)
                res['puom'] = l.product_uom_id
                res['uname'] = l.product_uom_id.name
                res['level'] = level
                res['code'] = l.bom_id.code
                result.append(res)
                if l.child_line_ids:
                    if level < 6:
                        level += 1
                    _get_rec(l.child_line_ids, level, qty=res['pqty'], uom=res['puom'])
                    if level > 0 and level < 6:
                        level -= 1
            return result

        children = _get_rec(object, level)

        return children
