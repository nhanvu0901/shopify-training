import requests
import werkzeug
import json

from pyatspi import selection

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
import urllib.parse
import shopify
import xmltodict
from datetime import datetime


class ShopifyShopXero(models.Model):
    _name = 'shopify.shop.xero'
    _rec_name = 'shop'

    shop = fields.Char('Shop')
    sp_shop_id = fields.Many2one('s.sp.shop')
    xero_token = fields.Char('Xero Token')

    sales_account_code = fields.Many2one("sales.account.code", string='Sales Account Code')
    payment_account_code = fields.Many2one("payment.account.code", string='Payment Account Code')
    shipping_account_code = fields.Many2one("shipping.account.code", string='Shipping Account Code')

    date_start = fields.Datetime('Date Start')
    date_end = fields.Datetime('Date End')

    products = fields.One2many('shopify.xero.products', 'shop_xero_id')
    orders = fields.One2many('shopify.xero.orders', 'shop_xero_id')

    shop_name = fields.Many2one('s.sp.shop', string="Shop name")
    discount_id = fields.Char(string="Discount ID")
    data = fields.Char(string="Data")
    def get_tenantID(self):
        if self.shop_name:
            enpointConect = 'https://api.xero.com/connections'
            store_info = request.env['s.sp.shop'].sudo().search([('domain', '=', self.shop_name.domain)], limit=1)
            # store_info = request.env['s.sp.shop'].sudo().search([('domain', '=', 'shoplify-odoo.myshopify.com')], limit=1)

            if store_info:
                header = {
                    "Authorization": "Bearer " + store_info.xero_access_token,
                    "Content-Type": "application/json"
                }
                response = requests.get(enpointConect, headers=header)
                tenantId = response.json()[0]['tenantId']
                return [tenantId, store_info.xero_access_token]
        else:
            return None

    def execute_mapping_data(self):

        self._get_account_code()

    def _get_account_code(self):
        sale_account = request.env['sales.account.code']
        payment_account = request.env['payment.account.code']
        shipping_account = request.env['shipping.account.code']

        if self.sales_account_code:
            record_set = request.env['sales.account.code'].search([])
            record_set.unlink()
        if self.payment_account_code:
            record_set = request.env['payment.account.code'].search([])
            record_set.unlink()

        if self.shipping_account_code:
            record_set = request.env['shipping.account.code'].search([])
            record_set.unlink()

        if self.shop_name:
            returnValue = self.get_tenantID()
            tenantId = returnValue[0]
            access_token = returnValue[1]

            enpoint = 'https://api.xero.com/api.xro/2.0/Accounts'
            headerAccount = {
                "Authorization": "Bearer " + access_token,
                "Content-Type": "application/json",
                "Xero-tenant-id": tenantId
            }
            responseAccount = requests.get(enpoint, headers=headerAccount)

            accountXML = responseAccount.text
            obj = xmltodict.parse(accountXML)

            json_string = json.dumps(obj)
            accounts = json.loads(json_string).get('Response').get('Accounts').get("Account")

            for account in accounts:
                if account.get("Type") == 'SAlES' or account.get("Type") == 'REVENUE':
                    # tuple = ('code', account.get("Code"))
                    # vals.append(tuple)
                    account_exist = sale_account.sudo().search([('code', '=', account.get("Code"))], limit=1)
                    if not account_exist:
                        account_exist.create({
                            'code': account.get("Code"),
                            'account_id': account.get("AccountID"),
                            'shop_name': self.shop_name.domain
                        })
                    else:
                        account_exist.write({
                            'code': account.get("Code"),
                            'account_id': account.get("AccountID"),
                            'shop_name': self.shop_name.domain
                        })

                if account.get("Type") == 'EXPENSE':
                    account_exist = payment_account.sudo().search([('code', '=', account.get("Code"))], limit=1)
                    if not account_exist:
                        account_exist.create({
                            'code': account.get("Code"),
                            'account_id': account.get("AccountID"),
                            'shop_name': self.shop_name.domain
                        })
                    else:
                        account_exist.write({
                            'code': account.get("Code"),
                            'account_id': account.get("AccountID"),
                            'shop_name': self.shop_name.domain
                        })
                if account.get("Type") == 'EQUITY':
                    account_exist = shipping_account.sudo().search([('code', '=', account.get("Code"))], limit=1)
                    if not account_exist:
                        account_exist.create({
                            'code': account.get("Code"),
                            'account_id': account.get("AccountID")
                        })
                    else:
                        account_exist.write({
                            'code': account.get("Code"),
                            'account_id': account.get("AccountID")
                        })
        else:
            return None
    def initShopifySession(self):
        # sp_api_key = request.env['ir.config_parameter'].sudo().get_param('bought_together.sp_api_key')
        # sp_api_secret_key = request.env['ir.config_parameter'].sudo().get_param('bought_together.sp_api_secret_key')
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
        api_version = request.env['ir.config_parameter'].sudo().get_param('test_shopi.api_version')

        shopify_app_exist = request.env['s.app'].sudo().search([('shop_url', '=', shop_url)], limit=1)

        new_session = shopify.Session(shop_url, api_version, token=shopify_app_exist.sp_access_token)
        shopify.ShopifyResource.activate_session(new_session)
        return new_session
    def fetch_product(self):
        self.initShopifySession()
        min = datetime.strftime(self.date_start, "%Y-%m-%d")
        max = datetime.strftime(self.date_end, "%Y-%m-%d")
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
        data_shopify = shopify.Product.find(published_at_min=min, published_at_max=max)
        for data in data_shopify:
            if data:
                print(data.id)

        enpoint = 'https://api.xero.com/connections'
        if self.shop_name:
            store_info = request.env['s.sp.shop'].sudo().search([('domain', '=', self.shop_name.domain)], limit=1)
            if store_info:
                header = {
                    "Authorization": "Bearer " + store_info.xero_access_token,
                    "Content-Type": "application/json"
                }
                response = requests.get(enpoint, headers=header)
                if response.status_code != 404:
                    if response.ok:
                        print(response.json())
                        return json.dumps({
                            "status": "success",
                            "result": response.json()
                        })

                    else:
                        data = response.json()

                        if 'Detail' in data:
                            if 'TokenExpired' in data['Detail']:
                                store_info.xero_refresh_token()
                                self.list_connection()
                            else:
                                return json.dumps({
                                    "error": data
                                })
                else:
                    return json.dumps({
                        "error": "Not Found"
                    })
        else:
            raise ValidationError(_("Choose the shop to fetch"))

    def fetch_order(self):
        print("Hello")

    def _display_redirect_xero(self):

        client_id = request.env['ir.config_parameter'].sudo().get_param('test_shopi.client_id')
        redirectURLXero = request.env['ir.config_parameter'].sudo().get_param('test_shopi.redirect_url_xero')
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
        redirectUrl = "https://login.xero.com/identity/connect/authorize?response_type=code&client_id=" + client_id + "&redirect_uri=" + redirectURLXero + "&scope=openid%20profile%20email%20accounting.transactions&state=" + shop_url
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': redirectUrl
        }

    def redirect_xero(self):
        client_id = request.env['ir.config_parameter'].sudo().get_param('test_shopi.client_id')
        redirectURLXero = request.env['ir.config_parameter'].sudo().get_param('test_shopi.redirect_url_xero')
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
        redirectUrl = "https://login.xero.com/identity/connect/authorize?response_type=code&client_id=" + client_id + "&redirect_uri=" + redirectURLXero + "&scope=openid%20profile%20email%20accounting.transactions&state=" + shop_url
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': redirectUrl
        }

    def redirect_to_sync_xero_page(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/xero/main',
        }

    def sync(self):
        # call xero api and sync data
        return True


class ShopifyShopXeroProducts(models.Model):
    _name = 'shopify.xero.products'
    _rec_name = 'product_name'

    product_id = fields.Char()
    product_name = fields.Char()
    product_handle = fields.Char()
    shop_xero_id = fields.Many2one('shopify.shop.xero')


class ShopifyShopXeroOrders(models.Model):
    _name = 'shopify.xero.orders'
    _rec_name = 'order_name'

    order_id = fields.Char()
    order_name = fields.Char()
    order_lines_data = fields.Char()
    shop_xero_id = fields.Many2one('shopify.shop.xero')


class ShopifyShopXeroFetchHistory(models.Model):
    _name = 'shopify.xero.fetch.history'

    status = fields.Char()
    count = fields.Integer()


class Xero(models.Model):
    _name = 'xero.model'
    _rec_name = 'id_xero_account'

    id_xero_account = fields.Char(string="ID")
    tenantId = fields.Char(string="Tenant Id")
    shop_shopify = fields.Many2one('s.sp.shop', string="Shop name")
    shopify_shop_url = fields.Char(string="Url")
    contact_id = fields.Char(string="Contact ID")
    xero_access_token = fields.Char(string="Access Token")


class Sales_account_code(models.Model):
    _name = "sales.account.code"
    _rec_name = 'code'
    code = fields.Char(string='Code')
    account_id = fields.Char(string="Account ID")
    shop_name = fields.Char(string="Shop name")


class Payment_account_code(models.Model):
    _name = "payment.account.code"
    _rec_name = 'code'
    code = fields.Char(string='Code')
    account_id = fields.Char(string="Account ID")
    shop_name = fields.Char(string="Shop name")


class Shipping_account_code(models.Model):
    _name = "shipping.account.code"
    _rec_name = 'code'
    code = fields.Char(string='Code')
    account_id = fields.Char(string="Account ID")


class TableHistoryOrder(models.Model):
    _name = "table.sync.history"

    invoice_id = fields.Char(string="Invoice ID")
    order_id = fields.Char(string="ID")
    total_money = fields.Char(string="Total money")
    order_name = fields.Char(string="Order name")
    list_history = fields.Many2many('invoice.history.record','record_id', string="List history sync")
    #

class HistoryRecord(models.Model):
    _name = "invoice.history.record"

    changes = fields.Char(string="Changes")
    date_update = fields.Char(string="Date update")
    Details = fields.Char(string="Details")
    record_id= fields.Char(string="ID")
    customer_name = fields.Char(string="Customer name")
