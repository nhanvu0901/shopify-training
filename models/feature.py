import json, xmltodict

import dateutil
import requests
import shopify
import time

from base64 import b64encode

from xero_python.api_client import ApiClient, Configuration
from xero_python.api_client.oauth2 import OAuth2Token

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime
import datetime as convertDate

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
        current_user = request.env.user
        shopify_shop_exist = request.env['s.sp.shop'].sudo().search([('user', '=', current_user.id)], limit=1)
        shop_app_exist = request.env['s.app'].sudo().search([('shop_url', '=', shopify_shop_exist.domain)], limit=1)
        if shopify_shop_exist:
            api_version = request.env['ir.config_parameter'].sudo().get_param('test_shopi.api_version')

            new_session = shopify.Session(shopify_shop_exist.domain, api_version, token=shop_app_exist.sp_access_token)
            shopify.ShopifyResource.activate_session(new_session)

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
                    product = (4, i)  # link to an existing record
                    list_product_id.append(product)

                customer = shopify.Order.find(order.id).customer

                order_exist = request.env['shop.orders'].sudo().search([('order_id', '=', order.id)], limit=1)
                if order_exist:
                    request.env['shop.orders'].sudo().write({
                        "customer_name": customer.first_name,
                        "product_list": list_product_id,  # linnk the id of product_list to product id
                        "order_id": order.id,
                        "order_name": order.name,
                        "created_at": order.created_at,
                        "order_address": order.shipping_address.address1,
                        "sum_money": order.total_price,
                        "store_name": order.order_status_url[8:35],
                        "financial_status": order.financial_status,
                        "total_tax": order.total_tax
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
                        "store_name": order.order_status_url.split("//")[1].split("/")[0],
                        "financial_status": order.financial_status,
                        "total_tax": order.total_tax

                    })



        else:
            raise ValidationError(_("Account not have any shopify store,log to another acc"))






    def shopify_fetch_product(self):
        global varient_price,varient_quantity,varient_id,product_image
        min = datetime.strftime(self.min_time, "%Y-%m-%d")
        max = datetime.strftime(self.max_time, "%Y-%m-%d")
        #

        current_user = request.env.user
        shopify_shop_exist = request.env['s.sp.shop'].sudo().search([('user', '=', current_user.id)], limit=1)
        shop_url =shopify_shop_exist.domain
        shop_app_exist = request.env['s.app'].sudo().search([('shop_url', '=', shopify_shop_exist.domain)], limit=1)
        if shopify_shop_exist:
            api_version = request.env['ir.config_parameter'].sudo().get_param('test_shopi.api_version')

            new_session = shopify.Session(shopify_shop_exist.domain, api_version, token=shop_app_exist.sp_access_token)
            shopify.ShopifyResource.activate_session(new_session)

            data_shopify = shopify.Product.find(published_at_min=min, published_at_max=max)

            for data in data_shopify:
                if data:

                    product_exist = request.env['shop.product'].sudo().search([('product_id', '=', data.get_id())], limit=1)
                    varient = shopify.Product.find(data.get_id()).variants
                    images = shopify.Product.find(data.get_id()).images

                    for i in varient:
                        varient_price = i.price
                        varient_quantity = i.inventory_quantity
                        varient_id = i.id
                    for i in  images:
                        product_image = i.src
                    if product_exist:
                        request.env['shop.product'].sudo().write({
                            "title": shopify.Product.find(data.get_id()).title,
                            "created_at": shopify.Product.find(data.get_id()).created_at,
                            "product_id": data.id,
                            "product_price": varient_price,
                            "store_name": shop_url,
                            "handle":'https://'+shop_url+'/products/'+ shopify.Product.find(data.get_id()).handle,
                            "quantity":varient_quantity,
                            "product_image":product_image,
                            "varient_id":varient_id
                        })
                    else:
                        request.env['shop.product'].sudo().create({
                            "title": shopify.Product.find(data.get_id()).title,
                            "created_at": shopify.Product.find(data.get_id()).created_at,
                            "product_id": data.id,
                            "product_price": varient_price,
                            "store_name": shop_url,
                             "handle":'https://'+shop_url+'/products/'+ shopify.Product.find(data.get_id()).handle,
                            "quantity":varient_quantity,
                            "product_image": product_image,
                            "varient_id": varient_id
                        })
        else:
            raise ValidationError(_("Account not have any shopify store,log to another acc"))


class ShopOrderProduct(models.Model):
    _name = 'shop.product'
    _rec_name = 'title'

    title = fields.Char("Title")
    product_id = fields.Char("Product ID")
    created_at = fields.Char("Publish At")
    product_price = fields.Char("Price")
    store_name = fields.Char("Store name")
    handle = fields.Char("Product URL")
    quantity = fields.Char("Quantity")
    product_image = fields.Char("Image url")
    varient_id = fields.Char("Varient_id")


class ShopOrder(models.Model):
    _name = 'shop.orders'

    customer_name = fields.Char("Customer's name")
    product_list = fields.Many2many('shop.product', 'product_id', string="Product list")
    order_id = fields.Char("ID")
    order_name = fields.Char("Order name")
    created_at = fields.Char("Date created")
    order_address = fields.Char("Order address")
    sum_money = fields.Char("Total momey")
    store_name = fields.Char("Store name")
    financial_status = fields.Char("Payment Status")
    total_tax = fields.Char("Total tax")

    # due_date = fields.Char("Due date")
    def sycn_order(self):
        xero_model = request.env['xero.model'].sudo().search([('shopify_shop_url', '=', self.store_name)], limit=1)

        line_items = []
        for product in self.product_list:
            price_product = int(product.product_price) + int(product.product_price) * 10 / 100

            data = {
                "Description": product.title,
                "UnitAmount": str(price_product),

            }

            line_items.append(data)

        # if (self.financial_status == 'paid'):
        invoice = {
            "Type": "ACCREC",
            "Contact": {
                "ContactID": xero_model.contact_id
            },
            "InvoiceNumber": self.order_id,
            "Date": self.created_at,
            "Status": "DRAFT",

            "LineItems": line_items}

        headerAccount = {
            "Authorization": "Bearer " + xero_model.xero_access_token,
            "Content-Type": "application/json",
            "Xero-tenant-id": xero_model.tenantId
        }
        endpoint = "https://api.xero.com/api.xro/2.0/Invoices"

        responseData = requests.post(url=endpoint, headers=headerAccount, data=json.dumps(invoice))
        print(responseData)


        obj = xmltodict.parse(responseData.text)
        if obj.get("Response").get("Invoices").get("Invoice").get("InvoiceID"):
            invoice_id = obj.get("Response").get("Invoices").get("Invoice").get("InvoiceID")
            if (self.financial_status == 'paid'):

                payment_account = request.env['sales.account.code'].sudo().search([('shop_name', '=', self.store_name)],
                                                                                    limit=1)
                if payment_account:
                    account_code = payment_account.code


                    line_itemsPost = []
                    for product in self.product_list:
                        price_product_post = int(product.product_price) + int(product.product_price) * 10 / 100

                        data = {
                            "Description": product.title,
                            "UnitAmount": str(price_product_post),
                            "AccountCode":account_code,
                            "TaxType": "NONE"
                        }

                        line_itemsPost.append(data)
                    invoice = {
                        "Type": "ACCREC",
                        "Contact": {
                            "ContactID": xero_model.contact_id
                        },
                        "InvoiceNumber": self.order_id,
                        "Date": self.created_at,
                        "DueDate": self.created_at,
                        "Status": "AUTHORISED",
                        "LineItems": line_itemsPost}

                    responseUpdate = requests.post(url=endpoint, headers=headerAccount, data=json.dumps(invoice))
                    print(responseUpdate)


                    payment_data = {
                        "Invoice": {"InvoiceID": invoice_id},
                        "Amount": self.sum_money,
                        "Account": { "Code":account_code  },
                    }
                    endpointPostData = "https://api.xero.com/api.xro/2.0/Payments"
                    reponsePayment = requests.post(url=endpointPostData, headers=headerAccount,
                                                   data=json.dumps(payment_data))
                    print(reponsePayment)
                else:
                    raise ValidationError(_("Choose the account for payment in the Xero fetch menu"))

            #get the hisr=tory record
            endpointHistory = "https://api.xero.com/api.xro/2.0/Invoices/"+invoice_id+"/History"
            responseHistory = requests.get(url=endpointHistory, headers=headerAccount)
            objHistory = xmltodict.parse(responseHistory.text)
            history_record = objHistory.get("Response").get('HistoryRecords')
            list_record = []
            list_record_id = []
            # ids = request.env['invoice.history.record'].search([]).ids
            # record_set = self.env['invoice.history.record'].search([('id', 'in', ids)])
            # record_set.unlink()

            for record in history_record.get('HistoryRecord'):
                history_record_table = request.env['invoice.history.record'].sudo().create({
                    "changes":record.get('Changes'),
                    'date_update':record.get('DateUTC'),
                    'Details':record.get('Details'),
                    'record_id':convertDate.datetime.now().strftime('%Y%m%d%H%M%S%f'),
                    'customer_name':self.customer_name
                })
                list_record.append(history_record_table.id)

            ids = request.env['invoice.history.record'].search([]).ids
            for i in ids:
                    for j in list_record:
                        if(j == i):
                            record = (4, j)  # link to an existing record
                            list_record_id.append(record)

            # for i in ids:
            #     for j in list_record:
            #         if j == i:
            #             record = (4, i)
            #             list_record_id.append(record)


            table_record = request.env['table.sync.history'].sudo().search([('invoice_id', '=', invoice_id)], limit=1)
            if table_record:
              table_record.list_history.unlink()
              table=  table_record.write({
                    "invoice_id": invoice_id,
                    "order_id": self.order_id,
                    "total_money": self.sum_money,
                    "order_name": self.order_name,
                    "list_history":list_record_id
                })
            else:
                table_record.create({
                    "invoice_id": invoice_id,
                    "order_id": self.order_id,
                    "total_money": self.sum_money,
                    "order_name": self.order_name,
                    "list_history": list_record_id
                })











# note create a total amount paid field for the paid acc
# retrieve the account id from the
# --> add vao payment
