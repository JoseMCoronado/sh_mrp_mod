# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ShippingAccount(models.Model):
    _inherit = 'x_customer.shipping.account'
    _description = "Customer Shipping Accounts"
    _order = "sequence asc"

    sequence = fields.Integer('Sequence', default=1, help="Lower is better.")
    x_acct_num = fields.Char(string="Account Number")
    x_carrier_id = fields.Many2one('delivery.carrier',string="Carrier")
    x_notes = fields.Char(string="Notes")
    x_partner_id = fields.Many2one('res.partner',string="Customer")
    x_zip = fields.Char(string="Billing Zip")
