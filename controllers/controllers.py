import binascii
import os
from base64 import b64encode

import requests
import shopify
import werkzeug.utils
import xmltodict
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
        print(kw)
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
        current_user = request.env['res.users'].sudo().search([('login', '=', kw['shop'])],
                                                              limit=1)
        if shopify_store_exist:
            shopify_store_exist.write(
                {
                    "shop_name": shop.name,
                    "domain": domain,
                    "currency": currency,
                    "country_name": country_name,
                    "email": email,
                    "shop_id": shop.id,
                    "user": current_user
                }
            )

        else:
            shopify_store_exist = shopify_store.create({
                "shop_name": shop.name,
                "domain": domain,
                "currency": currency,
                "country_name": country_name,
                "email": email,
                "user": current_user,
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
            request.env.ref('test_shopi.shopify_config_settings_menu').id)  # id of the menuitem

        return werkzeug.utils.redirect(redirectUrl)

    @http.route('/xero/authenticate/', auth='public', website=True, method=['GET'], csrf=False)
    def xero_authenticate(self, **kwargs):

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
                "redirect_uri": web_base_url + "/xero/authenticate/",
            }
            responce = requests.post(endpoint, headers=header, data=data)

            if responce.ok:
                data = responce.json()

            vals = {}
            valXeroModel = {}
            shopify_store_exist = request.env['s.sp.shop'].sudo().search([('domain', '=', state)], limit=1)
            if 'access_token' in data:
                vals['xero_access_token'] = data['access_token']
                valXeroModel['xero_access_token'] = data['access_token']

                enpointConect = 'https://api.xero.com/connections'

                header = {
                    "Authorization": "Bearer " + data['access_token'],
                    "Content-Type": "application/json"
                }
                response = requests.get(enpointConect, headers=header)

                valXeroModel["tenantId"] = response.json()[0]['tenantId']
                valXeroModel["id_xero_account"] = response.json()[0]['id']
                if shopify_store_exist:
                    valXeroModel["shop_shopify"] = shopify_store_exist.id
                    valXeroModel["shopify_shop_url"] = shopify_store_exist.domain

                # get the contact id
                endpointAcount = "https://api.xero.com/api.xro/2.0/Contacts"
                headerAccount = {
                    "Authorization": "Bearer " + data['access_token'],
                    "Content-Type": "application/json",
                    "Xero-tenant-id": response.json()[0]['tenantId']
                }
                responseAccount = requests.get(endpointAcount, headers=headerAccount)
                if responseAccount.ok:
                    accountXML = responseAccount.text
                    obj = xmltodict.parse(accountXML)
                    json_string = json.dumps(obj)
                    valXeroModel['contact_id'] = json.loads(json_string).get('Response').get("Contacts").get(
                        "Contact").get("ContactID")
                xero_model_exist = request.env['xero.model'].sudo().search(
                    [('id_xero_account', '=', response.json()[0]['id'])],
                    limit=1)
                if xero_model_exist:
                    xero_model_exist.write(valXeroModel)
                else:
                    xero_model_exist.create(valXeroModel)

            if 'refresh_token' in data:
                vals['xero_refresh_token'] = data['refresh_token']

            if shopify_store_exist:
                shopify_store_exist.write(vals)
            else:
                shopify_store_exist.create(vals)



            redirectUrl = web_base_url + '/web?#menu_id=' + str(
                request.env.ref('test_shopi.shopify_config_settings_menu').id)  # id of the menuitem

            return werkzeug.utils.redirect(redirectUrl)

    @http.route('/getdata',type='json', auth='none', cors='*', csrf=False, save_session=False)
    def get_store_front_end_data(self, **kwargs):
        if request.jsonrequest:
            global shop_name
            product_id = request.jsonrequest.get('product_id')
            product_handle = request.jsonrequest.get('product_handle')
            discount_combo = request.env['shopify.discount'].sudo().search([])

            combo_product =[]
            for combo in discount_combo:
                for product in combo.products:
                    if(product.product_id == str(product_id)):
                        combo_product.append(combo)

            list_combo=[]
            for combo in combo_product:
               discount_setting = request.env['shopify.discount.settings'].sudo().search([('store.domain', '=',combo.store_name)],limit=1)
               list_product=[]
               for product in combo.products:
                   item ={
                       "product_id":product.product_id,
                       "product_name":product.product_name,
                       "product_handle":product.product_handle,
                       "quantity":product.qty,
                       "product_price":product.product_price,
                       "image_url":product.image_url

                   }
                   list_product.append(item)

               if(discount_setting):
                  custom = {
                      "font_color": discount_setting.font_color,
                      "add_to_cart_color": discount_setting.add_to_cart_color,
                      "position": discount_setting.position,

                  }



               if(combo.discount_type == 'per'):
                   combo_data={
                       "discount_amount":str(combo.discount_amount)+"%",
                       "products":list_product,
                       "custom":custom
                   }
                   list_combo.append(combo_data)
               else:
                   combo_data={
                       "discount_amount": str(combo.discount_amount),
                       "products": list_product,
                       "custom": custom
                   }
                   list_combo.append(combo_data)

            return json.dumps(list_combo)



    def compare_combo(self,request):
        discount_combo = request.env['shopify.discount'].sudo().search([])

        if request.jsonrequest:

            item_list = request.jsonrequest.get("items")

            flag = None
            for combo in discount_combo:
                if (len(combo.products) == len(item_list)):
                    count = 0
                    for product in combo.products:
                        for item in item_list:
                            # product_exist = request.env['shopify.discount'].sudo().search(['&', ('combo.products.product_id', '=', item.get('product_id')), (combo.products.qty, '=', item.get('quantity'))],limit=1)
                            if product.product_id == str(item.get('product_id')) and product.qty == item.get(
                                    'quantity'):
                                # if product_exist:
                                count += 1

                        if count == len(item_list):
                            flag = combo
                            return flag;
    @http.route('/shopify/cart',type='json', auth='none', cors='*', csrf=False, save_session=False)
    def add_store_front_end_combo(self, **kwargs):#add to cart

        if request.jsonrequest:
            currency =request.jsonrequest.get('currency')
            flag = self.compare_combo(request)
            if flag:
                list_product = []
                for product in flag.products:
                    item = {
                        "product_id": product.product_id,
                        "product_name": product.product_name,
                        "product_handle": product.product_handle,
                        "quantity": product.qty,
                        "product_price": product.product_price,
                        "image_url": product.image_url,
                        "varient_id":product.varient_id
                    }
                    list_product.append(item)
                if (flag.discount_type == 'per'):
                    combo_data = {
                        "discount_amount": str(flag.discount_amount) + "%",
                        "products": list_product,
                        "currency":currency
                    }
                else:
                    combo_data = {
                        "discount_amount": str(flag.discount_amount),
                        "products": list_product,
                        "currency": currency
                    }

                return json.dumps(combo_data)

            else:
                print("False")


    @http.route('/shopify/checkout',type='json', auth='none', cors='*', csrf=False, save_session=False)
    def shopify_checkout(self, **kwargs):
        sp_api_key = request.env['ir.config_parameter'].sudo().get_param('test_shopi.sp_api_key')
        sp_api_secret_key = request.env['ir.config_parameter'].sudo().get_param('test_shopi.sp_api_secret_key')
        api_version = request.env['ir.config_parameter'].sudo().get_param('test_shopi.api_version')
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')

        # session = shopify.Session(shop_url, api_version)
        # access_token = session.request_token(request.params)
        # print(access_token)
        new_session = shopify.Session("shoplify-odoo.myshopify.com", "2021-10",
                                      token="shpua_f29fc106d85a039d1d3e44a4405ce179")
        shopify.ShopifyResource.activate_session(new_session)

        values = {}
        if(request.jsonrequest):

            list_product = json.loads(json.loads(request.jsonrequest['send']['responseText']).get('result'))['products']
            discount_value = json.loads(json.loads(request.jsonrequest['send']['responseText']).get('result'))['discount_amount']
            line_items = []
            for i in list_product:

                product = {
                    'variant_id' : int(i.get('varient_id')),
                    'quantity' : int(i.get('quantity'))
                }
                line_items.append(product)
            values['line_items'] = line_items
            if(discount_value[-1] == '%'):

                values['applied_discount'] = {

                      "description": "Combo product sale off "+discount_value,
                      "value": int(float(discount_value[0:len(discount_value)-1])),
                      "value_type": "percentage",
                }
            else:
                values['applied_discount'] = {

                    "description": "Combo product sale off " + discount_value +json.loads(json.loads(request.jsonrequest['send']['responseText']).get('result'))['currency'],
                    "value": int(float(discount_value[0:len(discount_value) - 1])),
                    "value_type": "percentage",
                }
            ordercreate = shopify.DraftOrder.create(values)

            return json.dumps(ordercreate.invoice_url)



    @http.route('/shopify/addtocart',type='json', auth='none', cors='*', csrf=False, save_session=False)
    def shopify_add_to_cart(self, **kwargs):
        if request.jsonrequest:
            flag = self.compare_combo(request)
            if flag:
                flag.write({
                    "number_add_to_cart":flag.number_add_to_cart +1
                })

        return json.dumps("hello")









