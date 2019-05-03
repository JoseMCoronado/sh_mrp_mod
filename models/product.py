# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    special_instructions = fields.Binary("Special Instructions")
    special_instructions_url = fields.Char("Special Instructions URL")

    @api.multi
    def compute_sale_price(self):
        for template in self:
            if template.product_variant_count == 1:
                price = template.product_variant_id.compute_sale_price()
                template.list_price = price


class ProductProduct(models.Model):
    _inherit = "product.product"

    special_instructions = fields.Binary(
        "Special Instructions", related="product_tmpl_id.special_instructions"
    )
    special_instructions_url = fields.Char(
        "Special Instructions URL", related="product_tmpl_id.special_instructions_url"
    )

    @api.multi
    def compute_sale_price(self):
        bom_obj = self.env["mrp.bom"]
        bom = bom_obj._bom_find(product=self)
        if bom:
            price = self._calc_price(bom)
            return price

    def _calc_price(self, bom):
        price = 0.0
        result, result2 = bom.explode(self, 1)
        for sbom, sbom_data in result2:
            if not sbom.attribute_value_ids:
                price += (
                    sbom.product_id.uom_id._compute_price(
                        sbom.product_id.list_price, sbom.product_uom_id
                    )
                    * sbom_data["qty"]
                )
        if price > 0:
            price = bom.product_uom_id._compute_price(
                price / bom.product_qty, self.uom_id
            )
        return price
