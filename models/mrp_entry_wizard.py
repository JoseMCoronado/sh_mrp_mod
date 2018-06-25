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
    generate_label = fields.Boolean(string="Generate Label")

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
            datas = {'ids' : [wiz.id]}
            if wiz.generate_label == True:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'sh_mrp_mod.report_rework_workorder',
                    'datas': datas,
                }

    @api.multi
    def next_wo(self):
        for wiz in self:
            wiz.workorder_id.state = 'done'
            wiz.workorder_id.on_rework = False
            wiz.workorder_to_id.state = 'ready'
            wiz.workorder_to_id.on_rework = True
            datas = {'ids' : [wiz.id]}
            if wiz.generate_label == True:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'sh_mrp_mod.report_rework_workorder',
                    'datas': datas,
                }


    @api.multi
    def rework_wo(self):
        for wiz in self:
            wiz.workorder_to_id.state = 'ready'
            wiz.workorder_to_id.reason = wiz.reason
            wiz.workorder_to_id.on_rework = True
            wiz.workorder_id.state = 'pending'
            datas = {'ids' : [wiz.id]}
            if wiz.generate_label == True:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'sh_mrp_mod.report_rework_workorder',
                    'datas': datas,
                }

    @api.onchange('type')
    def apply_domain(self):
        for wiz in self:
            ids = wiz.workorder_id.production_id.workorder_ids.ids
            domain = {'workorder_to_id': [('id', 'in', ids)]}
            return {'domain': domain}

class WorkOrderCompleteWizard(models.TransientModel):
    _name = "work.order.complete.wizard"
    _description = 'Work Order Complete Wizard'

    workorder_id = fields.Many2one('mrp.workorder', string="Workorder")
    user_id = fields.Many2one('res.users',string="User", required="1")

    @api.model
    def default_get(self, fields):
        res = super(WorkOrderCompleteWizard, self).default_get(fields)
        workorder_id = self.env['mrp.workorder'].browse(self.env.context.get('active_id'))
        res.update({'workorder_id': workorder_id.id})
        return res

    @api.onchange('workorder_id')
    def apply_domain(self):
        for wiz in self:
            ids = wiz.workorder_id.workcenter_id.user_ids.ids
            domain = {'user_id': [('id', 'in', ids)]}
            return {'domain': domain}

    @api.multi
    def complete_wo(self):
        for wiz in self:
            wiz.workorder_id.done_user = wiz.user_id
            wiz.workorder_id.record_production()
