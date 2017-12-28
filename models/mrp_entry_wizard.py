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

class WorkOrderHoldReasonWizard(models.TransientModel):
    _name = "work.order.hold.reason.wizard"
    _description = 'Work Order Entry Wizard'

    reason = fields.Text(string='Reason')
    workorder_id = fields.Many2one('mrp.workorder', string="Workorder")
    workorder_to_id = fields.Many2one('mrp.workorder', string="Next operation:")
    type = fields.Selection([
        ('rework', 'Rework'),
        ('send', 'End Rework'),
        ('hold', 'Hold')], string='State',
        copy=False, default='send')

    @api.model
    def default_get(self, fields):
        res = super(WorkOrderHoldReasonWizard, self).default_get(fields)
        workorder_id = self.env['mrp.workorder'].browse(self.env.context.get('active_id'))
        res.update({'workorder_id': workorder_id.id})
        return res

    @api.multi
    def hold_wo(self):
        for wiz in self:
            wiz.workorder_id.state = 'hold'
            wiz.workorder_id.reason = wiz.reason

    @api.multi
    def next_wo(self):
        for wiz in self:
            wiz.workorder_id.state = 'done'
            wiz.workorder_id.on_rework = False
            wiz.workorder_to_id.state = 'ready'
            wiz.workorder_to_id.on_rework = True

    @api.multi
    def rework_wo(self):
        for wiz in self:
            wiz.workorder_to_id.state = 'rework'
            wiz.workorder_to_id.reason = wiz.reason
            wiz.workorder_to_id.on_rework = True
            wiz.workorder_id.state = 'pending'

    @api.onchange('type')
    def apply_domain(self):
        for wiz in self:
            ids = wiz.workorder_id.production_id.workorder_ids.ids
            domain = {'workorder_to_id': [('id', 'in', ids)]}
            return {'domain': domain}
