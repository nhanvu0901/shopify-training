import shopify
import time
from odoo import models, fields, api
from odoo.tools.safe_eval import datetime

class SUser(models.Model):
    _inherit = 'res.users'
    sp_shop_id = fields.Char(string="Shop ID")




class SApp(models.Model):
    _name = 's.app'
    _description = 'Shopify App'
    _rec_name = "shop_url"

    shop_url = fields.Char(index=True)
    sp_api_key = fields.Char()
    sp_api_secret_key = fields.Char()
    sp_api_version = fields.Char()
    sp_access_token = fields.Char()
    # gg_api_client_id = fields.Char()
    # gg_api_client_secret = fields.Char()
    cdn_tag = fields.Char()


class Shopify(models.Model):
    _name = 's.sp.shop'
    _description = 'test_shopi.test_shopi'
    _rec_name = 'domain'

    email = fields.Char(string="Email")

    domain = fields.Char(string="Domain")
    currency = fields.Char(string="Currency")
    country_name = fields.Char(string="Country name")
    shop_name = fields.Char(string="Shop name")
    shop_id = fields.Char(string="Shop ID")
    user = fields.Many2one('res.users', "User")
    xero_access_token = fields.Char(string="Xero access token")
    xero_refresh_token = fields.Char(string="Xero refresh token")
    contact_id = fields.Char(string="Contact ID")


class SSpApp(models.Model):
    _name = 's.sp.app'  # shop app
    _rec_name = 'sp_shop_id'

    sp_shop_id = fields.Many2one('s.sp.shop')  # shopify shop
    s_app_id = fields.Many2one('s.app')  # shopify app

    token = fields.Char()

    # def add_webhook_to_shop(self, topic_name):
    #     self.ensure_one()
    #
    #     full_path = 'https://9dcd-222-252-29-196.ap.ngrok.io'
    #     webhook = shopify.Webhook()
    #     webhook.topic = topic_name
    #     webhook.address = full_path
    #     webhook.format = 'json'
    #     webhook.save()

    def add_script_tag_to_shop(self):
        src = self.s_app_id.cdn_tag
        shop_url = self.s_app_id.shop_url
        version = self.s_app_id.sp_api_version

        new_session = shopify.Session(shop_url, version,
                                      token='shpua_f29fc106d85a039d1d3e44a4405ce179')
        shopify.ShopifyResource.activate_session(new_session)

        scripTag = shopify.ScriptTag.find()
        for script in scripTag:
            if "Test.js" in script.src:
                script.destroy()
        if src:
            scripTagCreate = shopify.ScriptTag.create({
                "event": "onload",
                "src": src + "?v=" + str(time.time())
            })
            return scripTagCreate.id


