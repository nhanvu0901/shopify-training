
from odoo import models, fields, api


class Shopify(models.Model):

    _name = 'test_shopify'
    _description = 'test_shopi.test_shopi'


    email = fields.Char(string="Email" ,readonly=True)
    access_token = fields.Char(string="Access Token")
    domain = fields.Char(string="Domain")
    currency = fields.Char(string="Currency")
    country_name = fields.Char(string="Country name")
    email = fields.Char(string="Email")
    shop_name = fields.Char(string="Shop name")