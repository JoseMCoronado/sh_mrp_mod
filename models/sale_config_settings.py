# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    percent_markup = fields.Float(string="Percent Markup (%)", default=lambda self: self.env.user.company_id.percent_markup, related="company_id.percent_markup",store=False)
