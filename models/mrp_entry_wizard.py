# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class WorkOrderEntryWizard(models.TransientModel):
    _name = "work.order.entry.wizard"
    _description = 'Work Order Entry Wizard'

    quantity = fields.Float("Quantity Produced", required=True)
    operators = fields.Integer("# of Operators", required=True)
    workorder_id = fields.Many2one('mrp.workorder', string="Workorder")

    @api.model
    def default_get(self, fields):
        res = super(WorkOrderEntryWizard, self).default_get(fields)
        workorder_id = self.env['mrp.workorder'].browse(self.env.context.get('active_id'))
        res.update({'workorder_id': workorder_id.id})
        return res

    @api.multi
    def update_production(self):
        for wizard in self:
            wo = wizard.workorder_id
            wo.qty_producing = wizard.quantity
            wo.record_production()
            if wo.qty_produced < wo.qty_production:
                wo.button_pending()
            wo.time_ids[0].operators = wizard.operators
