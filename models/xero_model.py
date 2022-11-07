import werkzeug

from odoo import models, fields, api
from odoo.http import request
import urllib.parse


class ShopifyShopXero(models.Model):
    _name = 'shopify.shop.xero'
    _rec_name = 'shop'

    shop = fields.Char('Shop')
    sp_shop_id = fields.Many2one('s.sp.shop')
    xero_token = fields.Char('Xero Token')
    sales_account_code = fields.Char('Sales Account Code')
    payment_account_code = fields.Char('Payment Account Code')
    shipping_account_code = fields.Char('Shipping Account Code')

    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')

    # products = fields.One2many('shopify.product', 'shop_xero_id')
    # orders = fields.One2many('shopify.orders', 'shop_xero_id')

    def fetch_product(self):
        print('Xu ly fetch products tu shopify')
        # call api lay 10 products tuw shopify
        # luu vao database

    def fetch_order(self):
        print('Xu ly fetch products tu shopify')
        # call api lay 10 products tuw shopify
        # luu vao database

    def get_xero_token(self):
        # 1.redirect xero login
        try:
            from .auth import XeroAuth
            callback_url = '#base_url' + '/xero/authenticate'
            auth = XeroAuth(client_id='#client_id', client_secret='#client_secret', callback_uri=callback_url)
            auth_url = auth.generate_url()
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': auth_url,
            }
        except Exception as e:
            return e.__class__.__name__ + ': ' + str(e)

    def redirect_to_sync_xero_page(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/xero/main',
        }

    def sync(self):
        # call xero api and sync data
        return True

    def _display_redirect_xero(self):
        client_id = request.env['ir.config_parameter'].sudo().get_param('test_shopi.client_id')
        redirectURLXero = request.env['ir.config_parameter'].sudo().get_param('test_shopi.redirect_url_xero')
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
        redirectUrl = "https://login.xero.com/identity/connect/authorize?response_type=code&client_id=" + client_id + "&redirect_uri=" + redirectURLXero + "&scope=openid%20profile%20email%20accounting.transactions&state="+shop_url


        return {
            'type': 'ir.actions.act_url',
            'url': redirectUrl
        }
