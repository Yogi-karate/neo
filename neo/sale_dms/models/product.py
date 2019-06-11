from odoo import api, fields, models


class DmsProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    color_value = fields.Char('color', compute='_compute_color', help='test color', store=True)
    variant_value = fields.Char('variant', compute='_compute_variant', help='test something', store=True)

    @api.one
    @api.depends('attribute_value_ids')
    def _compute_color(self):
        for attribute_value in self.attribute_value_ids:
            if attribute_value.attribute_id.name.lower() == 'color':
                self.color_value = attribute_value.name

    @api.one
    @api.depends('attribute_value_ids')
    def _compute_variant(self):
        for attribute_value in self.attribute_value_ids:
            if attribute_value.attribute_id.name.lower() == 'variant':
                self.variant_value = attribute_value.name
