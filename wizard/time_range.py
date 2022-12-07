from odoo import api, models, fields, _

from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class WarrantyMassUpdate(models.TransientModel):
    _name = "combo.time.range"


    def multi_update(self):
        shopify_data = request.env['shopify.discount.data'].search(['&', ('date_create', '>=',self.date_from ), ('date_create', '<=', self.date_to)])
        for rec in shopify_data:
            shop_exist = request.env['shopify.discount.report'].sudo().search([('name', '=', rec.discount_id.name)], limit=1)
            if shop_exist:
                shop_exist.write({
                    "date_start": rec.date_create,
                    "name": rec.discount_id.name,
                    "total_revenue": rec.total_revenue,
                    "number_add_to_cart": rec.number_add_to_cart
                })
            else:
                shop_exist.create({
                    "date_start": rec.date_create,
                    "name": rec.discount_id.name,
                    "total_revenue": rec.total_revenue,
                    "number_add_to_cart": rec.number_add_to_cart

                })



    date_from = fields.Datetime(string="Date Start")
    date_to = fields.Datetime(string="Date End")