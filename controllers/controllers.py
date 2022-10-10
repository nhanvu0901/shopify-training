import binascii
import os

import shopify
import werkzeug.utils

from odoo.http import request

from odoo import http

import json
import random
import string

import werkzeug

from odoo import http
from odoo.http import request
import requests

SCOPES = '''read_products,
          read_customers,
          write_customers,
          read_third_party_fulfillment_orders,
          write_third_party_fulfillment_orders,
          read_orders,
          write_orders,
          write_draft_orders,
          read_draft_orders,
          write_script_tags,
          read_shipping,
          read_themes,
          write_themes,
          read_price_rules'''
class TestShopi(http.Controller):

    @http.route('/test_shopi', type='http', auth="public", website=True, method=['GET'], csrf=False)
    def index(self, **kw):

        # if 'shop' in kw:
        #     current_app = request.env.ref('app_external_id').sudo()
        #     api_key = current_app.sp_api_key,
        #     print(api_key)
        shopify.Session.setup(api_key="78e6382d4a5e2f2f37d5188204480b79", secret="0cc859187b6c7c7d82b1fd0e65683fd5")
        shop_url = "shoplify-odoo.myshopify.com"
        api_version = '2021-10'
        state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        redirect_uri = "http://localhost:8069/shopi"
        scopes = ['read_products', "read_customers", "write_customers", "read_third_party_fulfillment_orders",
                  "write_third_party_fulfillment_orders", "read_orders", "write_orders", "write_products",
                  "write_draft_orders", "read_draft_orders", "write_script_tags",
                  "read_shipping", "read_themes", "write_themes", "read_price_rules"]

        newSession = shopify.Session(shop_url, api_version)
        auth_url = newSession.create_permission_url(scopes, redirect_uri, state)

        return werkzeug.utils.redirect(auth_url)

    @http.route('/shopi', type='http', auth='none')
    def redirect(self, **kw):

        shop_url = kw['shop']

        api_version = '2021-07'
        session = shopify.Session(shop_url, api_version)

        access_token = session.request_token(request.params)

        new_session = shopify.Session(shop_url, api_version, access_token)

        shopify.ShopifyResource.activate_session(new_session)
        shop = shopify.Shop.current()

        domain = shop.domain
        currency = shop.currency
        country_name = shop.country_name
        email = shop.email

        shopify_model = request.env['s.sp.shop']

        shopify_exist = request.env['s.sp.shop'].sudo().search([('domain', '=', shop_url)], limit=1)

        if shopify_exist:
            shopify_exist.write(
                {
                    "access_token": access_token,
                    "shop_name": shop.name,
                    "domain": domain,
                    "currency": currency,
                    "country_name": country_name,
                    "email": email
                }
            )

        else:
            shopify_exist = shopify_model.create({
                "access_token": access_token,
                "shop_name": shop.name,
                "domain": domain,
                "currency": currency,
                "country_name": country_name,
                "email": email,
                "shop_id": shop.id
            })

            # shop_app = request.env['s.sp.app'].sudo().create({
            #     "sp_shop_id": shopify_exist,
            #
            # })
            topic = 'orders/updated'
            path = 'orders/create/%s' % shopify_exist.shop_id
            # shopify_exist.add_webhook_to_shop(topic, path)
            shopify_exist.add_webhook_to_shop(topic)

        print(shopify.Webhook.find())
        return "Hello, world"
