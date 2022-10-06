import binascii
import os

import shopify
import werkzeug.utils

from odoo.http import request

from odoo import http




class TestShopi(http.Controller):



    @http.route('/test_shopi', type='http', auth='none')
    def index(self, **kw):
        shopify.Session.setup(api_key="78e6382d4a5e2f2f37d5188204480b79", secret="0cc859187b6c7c7d82b1fd0e65683fd5")
        shop_url = "shoplify-odoo.myshopify.com"
        api_version = '2021-10'
        state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        redirect_uri = "http://localhost:8069/shopi"
        scopes = ['read_products', 'read_orders']

        newSession = shopify.Session(shop_url, api_version)
        auth_url = newSession.create_permission_url(scopes, redirect_uri, state)
        return werkzeug.utils.redirect(auth_url)

    @http.route('/shopi', type='http', auth='none')
    def redirect(self, **kw):
        shop_url = "shoplify-odoo.myshopify.com"
        api_version = '2021-10'
        session = shopify.Session(shop_url, api_version)

        access_token = session.request_token(request.params)
        print(access_token)
        new_session = shopify.Session(shop_url, api_version, access_token)

        shopify.ShopifyResource.activate_session(new_session)
        shop = shopify.Shop.current()

        domain = shop.domain
        currency = shop.currency
        country_name = shop.country_name
        email = shop.email
        print(domain+" "+currency+" "+country_name+" "+email+" ")

        shopify_model = request.env['test_shopify']
        shopify_search = request.env['test_shopify'].sudo().search([])
        flag = False

        for i in shopify_search:
            if(i.shop_name == shop.name):
                flag = True


        if(flag == False):
            shopify_model.create({
                "access_token": access_token,
                "shop_name": shop.name,
                "domain": domain,
                "currency": currency,
                "country_name": country_name,
                "email": email
            })

        return "Hello, world"

