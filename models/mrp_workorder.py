# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    sale_workorder_id = fields.Many2one('sale.workorder', 'Sale Workorder', readonly="1", store="1", related='production_id.sale_workorder_id')
    requested_date = fields.Datetime(string='Requested Date',
    readonly=True, store=True, index=True, copy=False,related='production_id.sale_workorder_id.requested_date')
    commitment_date = fields.Datetime(string='Commitment Date',
    readonly=True, store=True, index=True, copy=False,related='production_id.sale_workorder_id.commitment_date')
    done_user = fields.Many2one('res.users', string='Completed By')
    special_instructions = fields.Binary('Special Instructions', related='product_id.special_instructions', readonly=True)
    

    @api.multi
    def button_finish(self):
        super(MrpWorkorder, self).button_finish()
        if all(wo.state == 'done' for wo in self.production_id.workorder_ids):
            self.production_id.button_mark_done()

    @api.multi
    def record_production(self):
        super(MrpWorkorder, self).record_production()
        self.done_user = self.env.user
