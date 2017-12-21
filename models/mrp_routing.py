# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'
    
    initial_ops = fields.Boolean(
        'Initial Operation')
