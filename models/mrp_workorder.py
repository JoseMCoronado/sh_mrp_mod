# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    sale_workorder_id = fields.Many2one('sale.workorder', 'Sale Workorder', readonly="1", store="1", related='production_id.sale_workorder_id')

    @api.multi
    def button_finish(self):
        super(MrpWorkorder, self).button_finish()
        if all(wo.state == 'done' for wo in self.production_id.workorder_ids):
            self.production_id.button_mark_done()
