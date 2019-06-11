from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _



class DmsProduct(models.TransientModel):
    _name = 'dms.product'

    product_id = fields.Many2one('product.template', string='Product', ondelete="cascade")
    product_color = fields.Many2one('product.attribute.value', string='Color')
    product_variant = fields.Many2one('product.attribute.value', string='Variant')
    variant_attribute_values = fields.One2many('product.attribute.value', string='attributes',
                                               compute='compute_variant_attribute_values')
    color_attribute_values = fields.One2many('product.attribute.value', string='attributes',
                                             compute='compute_color_attribute_values')
    name = fields.Char(compute='_compute_name')

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        res = super(DmsProduct, self).create(vals)
        res.create_product_variant()
        return res



    @api.onchange('product_id')
    def compute_variant_attribute_values(self):
        if self.variant_attribute_values or self.color_attribute_values:
            self.product_variant = False
            self.product_color = False
        self.variant_attribute_values = None
        self.color_attribute_values = None
        products = self.sudo().env['product.template'].search([('id', '=', self.product_id.id)])
        if products.attribute_line_ids:
            self.variant_attribute_values = products.attribute_line_ids[1].value_ids
            print(self.variant_attribute_values)

    @api.onchange('product_variant')
    def compute_color_attribute_values(self):
        if self.color_attribute_values:
            self.product_color = False
            self.color_attribute_values = None
        if self.product_id:
            products = self.sudo().env['product.template'].search(
                [('id', '=', self.product_id.id)])
            self.color_attribute_values = products.attribute_line_ids[0].value_ids
        if self.product_variant and self.product_color:
            self._compute_name()


    def _compute_name(self):
            self.name = self.product_id.name+"(" +self.product_color.name+"," +self.product_variant.name+ ")"





    @api.multi
    def create_product_variant(self):
        template = self.env['product.template'].browse(self.product_id.id)
        existing_product = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id),
                                                      ('color_value', '=', self.product_color.name),
                                                      ('variant_value', '=', self.product_variant.name)], limit=1)
        if self.product_color.id == False or self.product_variant.id == False:
                raise UserError(_("One of the Product attributes is missing. Can't create!!!"))

        if existing_product:
            raise UserError(_("Product already exists"))
        else:
            attribute_line = self.env['product.template.attribute.line'].search([('product_tmpl_id','=',self.product_id.id)])
            if attribute_line :
                attribute_line [0].value_ids += self.product_color
                attribute_line [1].value_ids += self.product_variant
                template_values= {
                    'name': self.product_id.name,
                    'attribute_line_ids': [(6, '_', [attribute_line [0].id, attribute_line [1].id])]
                }
            else:
                raise UserError(_("There are no Template attributes. Please go back to Product screen and edit ",
                                  "You are not allowed create Template attributes here"))

            template.write(template_values)
            product = self.env['product.product']
            vals = {
                'name': template.name,
                'company_id': False,
                'product_tmpl_id': self.product_id.id,
                'attribute_value_ids'
                '': [(6, '_', [self.product_color.id, self.product_variant.id])],
                'display_name': self.name
            }
            product.create(vals)
