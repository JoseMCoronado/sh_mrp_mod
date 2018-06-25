# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    operators = fields.Integer('Operators', store=True)
    man_hours = fields.Float('Man Hours', compute='_compute_man_hours', store=True)

    @api.depends('operators', 'duration')
    def _compute_man_hours(self):
        for line in self:
            if line.operators > 0:
                line.man_hours = line.duration / line.operators

class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    user_ids = fields.Many2many('res.users',string="Users")

    @api.multi
    def open_sale_work_orders(self):
        for record in self:
            action_data = record.env.ref('sh_mrp_mod.action_sale_workorder_tree').read()[0]
            mos = record.order_ids.filtered(lambda x: x.state not in ['done','cancel']).mapped('production_id').ids
            action_data.update({'domain':[('manufacturing_ids','in',mos)],'context':{'workcenter':record.id}})
            return action_data
