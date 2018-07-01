# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = "res.company"

    percent_markup = fields.Float(string="Percent Markup (%)")
