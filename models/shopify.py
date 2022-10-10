import shopify

from odoo import models, fields, api
from odoo.tools.safe_eval import datetime





class Shopify(models.Model):
    _name = 's.sp.shop'
    _description = 'test_shopi.test_shopi'
    _rec_name = 'shop_name'

    email = fields.Char(string="Email", readonly=True)
    access_token = fields.Char(string="Access Token")
    domain = fields.Char(string="Domain")
    currency = fields.Char(string="Currency")
    country_name = fields.Char(string="Country name")
    shop_name = fields.Char(string="Shop name")
    shop_id=  fields.Char(string="Shop ID")
    def add_webhook_to_shop(self, topic_name):
        self.ensure_one()
        # full_path = '#base_url' + path
        # use ngrok https test tren local
        # print(path)
        full_path = 'https://9dcd-222-252-29-196.ap.ngrok.io'
        webhook = shopify.Webhook()
        webhook.topic = topic_name
        webhook.address = full_path
        webhook.format = 'json'
        webhook.save()





