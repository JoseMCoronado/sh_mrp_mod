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
