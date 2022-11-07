import shopify
import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.safe_eval import datetime
from datetime import datetime


class Fetch_order(models.Model):
    _name = 'fetch.orders'

    min_time = fields.Datetime("Time start")
    max_time = fields.Datetime("Time end")

    min_time_order = fields.Datetime("Time start")
    max_time_order = fields.Datetime("Time end")

    # @api.depends('min_time', 'max_time')
    # def _fetch_data(self):
    #     # shopify.Order.find(created_at_min="2020-07-01", created_at_max="2020-07-15")
    #     print(self.min_time)
    def shopify_fetch_order(self):
        min = datetime.strftime(self.min_time_order, "%Y-%m-%d")
        max = datetime.strftime(self.max_time_order, "%Y-%m-%d")

        order_shopify = shopify.Order.find(published_at_min=min, published_at_max=max, status='any')
        list_product = []
        list_product_id = []
        for order in order_shopify:

            for product in order.line_items:
                product_exist = request.env['shop.product'].sudo().search([('product_id', '=', product.product_id)],
                                                                          limit=1)
                if product_exist:
                    list_product.append(product_exist.id)

            for i in list_product:
                product = (4, i) #link to an existing record
                list_product_id.append(product)

            customer = shopify.Order.find(order.id).customer

            order_exist = request.env['shop.orders'].sudo().search([('order_id', '=', order.id)], limit=1)
            if order_exist:
                request.env['shop.orders'].sudo().write({
                    "customer_name": customer.first_name,
                    "product_list": list_product_id, #linnk the id of product_list to product id
                    "order_id": order.id,
                    "order_name": order.name,
                    "created_at": order.created_at,
                    "order_address": order.shipping_address.address1,
                    "sum_money": order.total_price,
                })
            else:
                request.env['shop.orders'].sudo().create({
                    "customer_name": customer.first_name,
                    "product_list": list_product_id,
                    "order_id": order.id,
                    "order_name": order.name,
                    "created_at": order.created_at,
                    "order_address": order.shipping_address.address1,
                    "sum_money": order.total_price,
                })

    def shopify_fetch_product(self):
        global varient_price
        min = datetime.strftime(self.min_time, "%Y-%m-%d")
        max = datetime.strftime(self.max_time, "%Y-%m-%d")
        shop_url = request.env['ir.config_parameter'].sudo().get_param('test_shopi.shop_url')
        data_shopify = shopify.Product.find(published_at_min=min, published_at_max=max)

        for data in data_shopify:
            if data:
                print(data.id)
                product_exist = request.env['shop.product'].sudo().search([('product_id', '=', data.get_id())], limit=1)
                varient = shopify.Product.find(data.get_id()).variants
                for i in varient:
                    varient_price = i.price

                if product_exist:
                    request.env['shop.product'].sudo().write({
                        "title": shopify.Product.find(data.get_id()).title,
                        "created_at": shopify.Product.find(data.get_id()).created_at,
                        "product_id": data.id,
                        "product_price": varient_price,
                        "store_name": shop_url
                    })
                else:
                    request.env['shop.product'].sudo().create({
                        "title": shopify.Product.find(data.get_id()).title,
                        "created_at": shopify.Product.find(data.get_id()).created_at,
                        "product_id": data.id,
                        "product_price": varient_price,
                        "store_name": shop_url
                    })


class ShopOrderProduct(models.Model):
    _name = 'shop.product'

    title = fields.Char("Title")
    product_id = fields.Char("Product ID")
    created_at = fields.Char("Publish At")
    product_price = fields.Char("Price")
    store_name = fields.Char("Store name")


class ShopOrder(models.Model):
    _name = 'shop.orders'

    customer_name = fields.Char("Customer's name")
    product_list = fields.Many2many('shop.product', 'product_id', string="Product list")
    order_id = fields.Char("ID")
    order_name = fields.Char("Order name")
    created_at = fields.Char("Date created")
    order_address = fields.Char("Order address")
    sum_money = fields.Char("Total momey")
