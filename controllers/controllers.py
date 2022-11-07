import binascii
import os
from base64 import b64encode

import requests
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


class TestShopi(http.Controller):

    @http.route('/test_shopi', type='http', auth="public", website=True, method=['GET'], csrf=False)
    def index(self, **kw):
        sp_api_key = request.env['ir.config_parameter'].sudo().get_param('test_shopi.sp_api_key')
        sp_api_secret_key = request.env['ir.config_parameter'].sudo().get_param('test_shopi.sp_api_secret_key')
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
        api_version = request.env['ir.config_parameter'].sudo().get_param('test_shopi.api_version')
        redirect_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.redirect_url')

        shopify.Session.setup(api_key=sp_api_key, secret=sp_api_secret_key)
        shop_url = shop_url

        state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        redirect_uri = redirect_url
        scopes = ['read_products', "read_customers", "write_customers", "read_third_party_fulfillment_orders",
                  "write_third_party_fulfillment_orders", "read_orders", "write_orders", "write_products",
                  "write_draft_orders", "read_draft_orders", "write_script_tags", "read_script_tags",
                  "read_shipping", "read_themes", "write_themes", "read_price_rules"]

        newSession = shopify.Session(shop_url, api_version)
        auth_url = newSession.create_permission_url(scopes, redirect_uri, state)

        return werkzeug.utils.redirect(auth_url)

    @http.route('/shopi', type='http', auth='public')
    def redirect(self, **kw):

        cdn_tag = request.env['ir.config_parameter'].sudo().get_param('test_shopi.cdn_tag')
        sp_api_key = request.env['ir.config_parameter'].sudo().get_param('test_shopi.sp_api_key')
        sp_api_secret_key = request.env['ir.config_parameter'].sudo().get_param('test_shopi.sp_api_secret_key')
        api_version = request.env['ir.config_parameter'].sudo().get_param('test_shopi.api_version')
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')



        # session = shopify.Session(shop_url, api_version)
        # access_token = session.request_token(request.params)
        # print(access_token)

        shopify.Session.setup(
            api_key=sp_api_key,
            secret=sp_api_secret_key)
        shopify_session = shopify.Session(shop_url, api_version)
        access_token = shopify_session.request_token(kw)
        shopify.ShopifyResource.activate_session(shopify_session)

        shop = shopify.Shop.current()

        domain = shop.domain
        currency = shop.currency
        country_name = shop.country_name
        email = shop.email

        shopify_app = request.env['s.app']
        shopify_app_exist = request.env['s.app'].sudo().search([('sp_access_token', '=', access_token)], limit=1)
        if shopify_app_exist:
            shopify_app_exist.write({
                "shop_url": domain,
                "sp_api_key": sp_api_key,
                "sp_api_secret_key": sp_api_secret_key,
                "sp_api_version": api_version,
                "sp_access_token": access_token,
                "cdn_tag": cdn_tag
            })
        else:
            shopify_app_exist = shopify_app.create({
                "shop_url": domain,
                "sp_api_key": sp_api_key,
                "sp_api_secret_key": sp_api_secret_key,
                "sp_api_version": api_version,
                "sp_access_token": access_token,
                "cdn_tag": cdn_tag
            })

        shopify_store = request.env['s.sp.shop']

        shopify_store_exist = request.env['s.sp.shop'].sudo().search([('domain', '=', shop_url)], limit=1)

        if shopify_store_exist:
            shopify_store_exist.write(
                {

                    "shop_name": shop.name,
                    "domain": domain,
                    "currency": currency,
                    "country_name": country_name,
                    "email": email,
                    "shop_id": shop.id
                }
            )

        else:
            shopify_store_exist = shopify_store.create({
                "shop_name": shop.name,
                "domain": domain,
                "currency": currency,
                "country_name": country_name,
                "email": email,
                "shop_id": shop.id
            })

        shop_app = request.env['s.sp.app']
        shop_app_exist = request.env['s.sp.app'].sudo().search([('token', '=', access_token)], limit=1)

        if shop_app_exist:
            shop_app_exist.write({
                "sp_shop_id": shopify_store_exist.id,
                "s_app_id": shopify_app_exist.id,
                "token": access_token
            })
        else:
            shop_app_exist = shop_app.create({
                "sp_shop_id": shopify_store_exist.id,
                "s_app_id": shopify_app_exist.id,
                'token': access_token
            })
        shop_app_exist.add_script_tag_to_shop()

        # Cau4

        letters = string.ascii_lowercase
        password_generate = ''.join(random.choice(letters) for i in range(30))
        current_user = request.env['res.users'].sudo().search([('login', '=', kw['shop'])],
                                                              limit=1)
        if not current_user:

            current_company = request.env['res.company'].sudo().search([('name', '=', kw['shop'])], limit=1)
            if not current_company:
                currency_id = request.env['res.currency'].sudo().search(
                    ['&', '|', ('active', '=', False), ('active', '=', True), ('name', '=', currency)], limit=1)
                current_company = request.env['res.company'].sudo().create({
                    'name': kw['shop'],
                    'currency_id': currency_id.id
                })

            request.env['res.users'].sudo().create({
                'name': kw['shop'],
                'login': kw['shop'],
                'password': password_generate,
                'sp_shop_id': shop.id,
                'company_id': current_company.id,
                'company_ids': [(6, 0, [current_company.id])],
            })
        web_base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        redirectUrl = web_base_url + '/web?#menu_id=' + str(
            request.env.ref('test_shopi.shopify_config_settings_menu').id) # id of the menuitem

        return werkzeug.utils.redirect(redirectUrl)




    @http.route('/xero/authenticate/', auth='public')
    def xero_authenticate(self, **kwargs):
        print(kwargs)
        if 'code' in kwargs:
            web_base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            client_id = request.env['ir.config_parameter'].sudo().get_param('test_shopi.client_id')
            client_secret = request.env['ir.config_parameter'].sudo().get_param('test_shopi.client_secret')
            code = kwargs['code']
            state = kwargs['state']
            endpoint = 'https://identity.xero.com/connect/token'
            header = {
                "authorization": "Basic " + b64encode(str(client_id + ":" + client_secret).encode('ascii')).decode(
                    'utf-8'),
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": web_base_url + "/xero/authenticate/"
            }
            responce = requests.post(endpoint, headers=header, data=data)

            if responce.ok:
                data = responce.json()
                print(data)

            vals = {}
            if 'access_token' in data:
                vals['xero_access_token'] = data['access_token']
            if 'refresh_token' in data:
                vals['xero_refresh_token'] = data['refresh_token']
            shopify_store_exist = request.env['s.sp.shop'].sudo().search([('domain', '=', state)], limit=1)
            if shopify_store_exist:
                shopify_store_exist.write(vals)

            redirectUrl = web_base_url + '/web?#menu_id=' + str(
                request.env.ref('test_shopi.shopify_config_settings_menu').id)  # id of the menuitem

            return werkzeug.utils.redirect(redirectUrl)
