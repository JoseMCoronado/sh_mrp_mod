# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    sale_workorder_id = fields.Many2one('sale.workorder', 'Sale Workorder', readonly="1", store="1", related='production_id.sale_workorder_id')
    requested_date = fields.Datetime(string='Requested Date',
    readonly=True, store=True, index=True, copy=False,related='production_id.sale_workorder_id.requested_date')
    commitment_date = fields.Datetime(string='Commitment Date',
    readonly=True, store=True, index=True, copy=False,related='production_id.sale_workorder_id.commitment_date')
    done_user = fields.Many2one('res.users', string='Completed By')
    special_instructions = fields.Binary('Special Instructions', related='product_id.special_instructions', readonly=True)
    attribute_id = fields.Many2one('line.attribute','Custom Attributes', compute='_compute_attribute', store=False)
    sale_order_line_desc = fields.Text('Sale Line Desc', related='attribute_id.order_line.name',readonly=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('rework', 'Rework'),
        ('hold', 'On Hold'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], string='Status',
        default='pending')
    reason = fields.Text(string='Reason')
    on_rework = fields.Boolean(string='Rework')
    product_kit_id = fields.Many2one('product.product', string='Kit Product', related="production_id.product_kit_id")
    product_desc = fields.Char('Description',related="product_id.name")
    image = fields.Binary(string="Image",related="product_id.image")

    @api.multi
    def button_not_hold(self):
        for wo in self:
            wo.state = 'ready'

    @api.multi
    def button_finish(self):
        super(MrpWorkorder, self).button_finish()
        self.on_rework = False
        if any(r.state in ['done','progress'] for r in self.production_id.workorder_ids):
            self.production_id.state = 'progress'
        if all(wo.state == 'done' for wo in self.production_id.workorder_ids):
            self.production_id.state = 'done'
            self.production_id.button_mark_done()
        if all(r.state in ['cancel'] for r in self.production_id.workorder_ids):
            self.production_id.state = 'cancel'

    @api.depends('sale_workorder_id')
    def _compute_attribute(self):
        for line in self:
            #TODO What if they order the same gauge twice with different configuration?
            if line.sale_workorder_id:
                order_lines = line.sale_workorder_id.order_id.order_line.filtered(lambda r: r.product_id == line.product_id)
                if order_lines:
                    line.attribute_id = order_lines[0].attribute_id


    @api.multi
    def open_attribute_values(self):
        self.ensure_one()
        for line in self:
                action_data = line.env.ref('sh_line_attribute.action_window_line_attribute').read()[0]
                action_data.update({'res_id':line.attribute_id.id})
                return action_data
