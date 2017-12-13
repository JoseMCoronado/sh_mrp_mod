# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def print_packing_slip(self):
        for picking in self:
            active_id = picking.id
            datas = {'ids' : [active_id]}
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'sh_mrp_mod.report_packingslip',
                'datas': datas,
            }
