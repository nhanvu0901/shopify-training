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
                "Accept": "application/json",
                "Xero-tenant-id": tenantId
            }
            responseAccount = requests.get(enpoint, headers=headerAccount)


            accounts = json.loads(responseAccount.text).get('Accounts')

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
            raise ValidationError(_("Choose the shop to fetch"))
    # def initShopifySession(self):
    #     # sp_api_key = request.env['ir.config_parameter'].sudo().get_param('bought_together.sp_api_key')
    #     # sp_api_secret_key = request.env['ir.config_parameter'].sudo().get_param('bought_together.sp_api_secret_key')
    #     shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
    #     api_version = request.env['ir.config_parameter'].sudo().get_param('test_shopi.api_version')
    #
    #     shopify_app_exist = request.env['s.app'].sudo().search([('shop_url', '=', shop_url)], limit=1)
    #
    #     new_session = shopify.Session(shop_url, api_version, token=shopify_app_exist.sp_access_token)
    #     shopify.ShopifyResource.activate_session(new_session)
    #     return new_session
    def fetch_product(self):
        sp_api_secret_key = request.env['ir.config_parameter'].sudo().get_param('test_shopi.sp_api_secret_key')
        shop_app_exist = request.env['s.app'].sudo().search([('sp_api_secret_key', '=', sp_api_secret_key)], limit=1)

        shop_app_exist.initShopifySession(self.shop_name)

        min = datetime.strftime(self.date_start, "%Y-%m-%d")
        max = datetime.strftime(self.date_end, "%Y-%m-%d")

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
       if self.shop_name.domain and self.date_end and self.date_start:
           shopify_xero_order = request.env['shopify.xero.orders'].search([])
           if self.orders:
               shopify_xero_order.unlink()

           xero_model = request.env['xero.model'].sudo().search([('shopify_shop_url', '=', self.shop_name.domain)],
                                                                limit=1)
           header = {
               "Authorization": "Bearer " + xero_model.xero_access_token,
               "Accept": "application/json",
               "Xero-Tenant-Id": xero_model.tenantId,

           }

           enpoint = "https://api.xero.com/api.xro/2.0/Invoices"
           min = datetime.strftime(self.date_start, "%Y,%m,%d")
           max = datetime.strftime(self.date_end, "%Y,%m,%d")
           param = {"where" :"Date >=DateTime("+min+")"+" && Date<DateTime(" +max+")",

                    }
           response = requests.get(enpoint, headers=header,params=param)

           # Type = fields.Char()
           # InvoiceID = fields.Char()
           # AmountDue = fields.Char()
           # customer_name = fields.Char(string="Customer name")
           # shop_owner_name = fields.Char(string="Shop Owner Name")
           # date_create = fields.Char()

           for invoice in json.loads(response.content).get('Invoices'):
               shopify_xero_order.create({
                   "Type":invoice.get('Type'),
                   "InvoiceID": invoice.get('InvoiceID'),
                   "AmountDue": invoice.get('AmountDue'),
                   "customer_name": invoice.get('Reference'),
                   "contact_name": invoice.get('Contact').get('Name'),
                   "date_create": invoice.get('DateString'),
                   "shop_xero_id":self.id
               })


       else:
              raise ValidationError(_("Choose the shop to fetch"))


    def _display_redirect_xero(self):

        client_id = request.env['ir.config_parameter'].sudo().get_param('test_shopi.client_id')
        redirectURLXero = request.env['ir.config_parameter'].sudo().get_param('test_shopi.redirect_url_xero')
        sp_api_secret_key = request.env['ir.config_parameter'].sudo().get_param('test_shopi.sp_api_secret_key')

        shopify_app = request.env['s.app'].sudo().search([('sp_api_secret_key', '=', sp_api_secret_key)], limit=1)
        shop_app =  request.env['s.sp.app'].sudo().search([('s_app_id.id', '=', shopify_app.id)], limit=1)
        redirectUrl = "https://login.xero.com/identity/connect/authorize?response_type=code&client_id=" + client_id + "&redirect_uri=" + redirectURLXero + "&scope=openid%20profile%20email%20accounting.transactions%20accounting.contacts%20accounting.settings%20offline_access&state=" +shop_app.sp_shop_id.domain
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': redirectUrl
        }

    def redirect_xero(self):
        client_id = request.env['ir.config_parameter'].sudo().get_param('test_shopi.client_id')
        redirectURLXero = request.env['ir.config_parameter'].sudo().get_param('test_shopi.redirect_url_xero')
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
        redirectUrl = "https://login.xero.com/identity/connect/authorize?response_type=code&client_id=" + client_id + "&redirect_uri=" + redirectURLXero + "&scope=openid%20profile%20email%20accounting.transactions%20offline_access&state=" + shop_url
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

    shop_xero_id = fields.Many2one('shopify.shop.xero')
    Type = fields.Char()
    InvoiceID = fields.Char()
    AmountDue = fields.Char()
    customer_name = fields.Char(string="Customer name")
    contact_name = fields.Char(string="Contact Name")
    contact_id = fields.Char()
    date_create = fields.Char()





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
