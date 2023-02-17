import shopify
import time
from odoo import models, fields, api
from odoo.http import request
from odoo.tools.safe_eval import datetime

class SUser(models.Model):
    _inherit = 'res.users'
    sp_shop_id = fields.Char(string="Shop ID")




class SApp(models.Model):
    _name = 's.app'
    _description = 'Shopify App'
    _rec_name = "sp_access_token"




    sp_api_key = fields.Char()
    sp_api_secret_key = fields.Char()
    sp_api_version = fields.Char()
    sp_access_token = fields.Char()
    # gg_api_client_id = fields.Char()
    # gg_api_client_secret = fields.Char()
    cdn_tag = fields.Char()

    @api.model
    def initShopifySession(self, shopUrl):
        # sp_api_key = request.env['ir.config_parameter'].sudo().get_param('bought_together.sp_api_key')
        # sp_api_secret_key = request.env['ir.config_parameter'].sudo().get_param('bought_together.sp_api_secret_key')

        api_version = self.env['ir.config_parameter'].sudo().get_param('bought_together.api_version_bought_together')

        new_session = shopify.Session(shopUrl, api_version, token=self.sp_access_token)
        shopify.ShopifyResource.activate_session(new_session)
        return new_session


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
    setting = fields.Many2one('shopify.discount.settings',string='Setting')
    discount_combo = fields.One2many('shopify.discount','shopify_shop',string='Discount combo')



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

    # def add_script_tag_to_shop(self):
    #     src = self.s_app_id.cdn_tag
    #     shop_url = self.s_app_id.shop_url
    #     version = self.s_app_id.sp_api_version
    #     shop_app_url = request.env['s.sp.app'].sudo().search([('s_app_id.shop_url', '=', shop_url)], limit=1)
    #
    #     new_session = shopify.Session(shop_url, version,
    #                                   token=shop_app_url.token)
    #     shopify.ShopifyResource.activate_session(new_session)
    #
    #     scripTag = shopify.ScriptTag.find()
    #     for script in scripTag:
    #         if "Test.js" in script.src:
    #             script.destroy()
    #     if src:
    #         scripTagCreate = shopify.ScriptTag.create({
    #             "event": "onload",
    #             "src": src + "?v=" + str(time.time())
    #         })
    #         return scripTagCreate.id




