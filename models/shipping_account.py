# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ShippingAccount(models.Model):
    _inherit = 'x_customer.shipping.account'
    _description = "Customer Shipping Accounts"
    _order = "sequence asc"

    sequence = fields.Integer('Sequence', default=1, help="Lower is better.")
    x_acct_num = fields.Char(string="Account Number")
    x_carrier_id = fields.Many2one('delivery.carrier',string="Carrier")
    x_name = fields.Char(string="Name",compute="_compute_name",readonly=True)
    x_notes = fields.Char(string="Notes")
    x_partner_id = fields.Many2one('res.partner',string="Customer")
    x_zip = fields.Char(string="Billing Zip")

    @api.depends('x_partner_id','x_acct_num','x_carrier_id')
    def _compute_name(self):
        for record in self:
            if record.x_partner_id and record.x_acct_num and record.x_carrier_id:
                record.x_name = "%s %s %s" % (record.x_partner_id,ecord.x_acct_num,record.x_carrier_id)
