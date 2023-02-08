import json

from odoo import models, fields, api, http
from odoo.http import request
from datetime import datetime

class SAppDiscount(models.Model):
    _name = 'shopify.discount'
    _rec_name = 'name'

    name = fields.Char(index=True)
    discount_type = fields.Selection([('per', '%'), ('amount', 'Amount')], default='per', required=True)
    discount_amount = fields.Float()
    products = fields.One2many('shopify.discount.products', 'shop_discount_id')
    shopify_shop = fields.Many2one('s.sp.shop')
    store_name = fields.Char(string='Store name', related='shopify_shop.domain')


class SAppDiscountProduct(models.Model):
    _name = 'shopify.discount.products'
    product_fetch = fields.Many2one('shop.product', string="Product")
    shop_discount_id = fields.Many2one('shopify.discount')
    product_id = fields.Char(string="Product ID", related='product_fetch.product_id')
    product_name = fields.Char(string="Product name", related='product_fetch.title')
    product_handle = fields.Char(string="Product handle", related='product_fetch.handle')
    qty = fields.Integer(string="Amount of product apply discount")
    product_price = fields.Char(string="Product price", related="product_fetch.product_price")
    image_url = fields.Char(string="Images url", related="product_fetch.product_image")
    varient_id = fields.Char(string="Varient ID", related="product_fetch.varient_id")
    store_name = fields.Char(string="Shop name", related="product_fetch.store_name")


class SAppDiscountSettings(models.Model):
    _name = 'shopify.discount.settings'

    font_color = fields.Char(default='#FFFF')
    add_to_cart_color = fields.Char(default='#FFFF', string='Add to cart color')
    position = fields.Char(default='bottom')
    store = fields.One2many('s.sp.shop', 'setting', string='Store name')


class SAppDiscountData(models.Model):
    _name = 'shopify.discount.data'

    discount_id = fields.Many2one('shopify.discount')

    # number_add_to_cart = fields.Integer(string='Total number add to cart')
    sale = fields.Char(string='Sale Amount')
    date_create = fields.Datetime(string="Date Created")
    # total_revenue = fields.Float(string="Total Revenue")
    price_off = fields.Float(string="Price Off")






class SAppDiscountDataReport(models.Model):
    _name = 'shopify.discount.report'
    discount_id = fields.Many2one('shopify.discount')
    date_end = fields.Datetime(string="Date End")
    date_start = fields.Datetime(string="Date Created")
    shopify_count =  fields.One2many('shopify.discount.count','shopify_report')
    flag = fields.Boolean(default=False)
    html_iframe = fields.Html(compute="get_iframe",sanitize=False,string="Sale combo chart")

    @api.depends('discount_id', 'date_end', 'date_start', 'shopify_count')
    def get_iframe(self):
        if self.flag == True and self.id:

                self.html_iframe = '<iframe src="/shopify/discount/chart?shopify_discount_id=' + str(self.id) + '" width="800px" height="400px" border="none" "></iframe>'
        else:

                self.html_iframe = '<iframe  width="800px" height="400px"></iframe>'

    def anilytic(self):
       if len(self.shopify_count) ==0:
           if self.discount_id and self.date_end and self.date_start:
               # tim duoc bundle cung id
               find_bundle_data = request.env['shopify.discount.data'].search(['&', ('date_create', '>=',self.date_start ), ('date_create', '<=', self.date_end),('discount_id.id','=',self.discount_id.id)])
               if find_bundle_data:
                   #loc bundle de no co cung ngay
                   list_data={}
                   for data in find_bundle_data:
                      if data.date_create.strftime("%m/%d/%Y") not in list_data.keys():
                          list_data[data.date_create.strftime("%m/%d/%Y")] = [data.date_create,1,data]
                      else :
                          list_data[data.date_create.strftime("%m/%d/%Y")] = [data.date_create, list_data.get(data.date_create.strftime("%m/%d/%Y"))[1]+1,data]
                          print(list_data)
                   find_bundle_data = request.env['shopify.discount.count']

                   for item in list_data:
                       if list_data.get(item)[1] >1:#neu so lan add to cart >1
                           find_bundle_data.create({
                               "bundle_id":list_data.get(item)[2].discount_id.id,
                               "discount_id":list_data.get(item)[2].id,
                               "number_add_to_cart":list_data.get(item)[1],
                               "sale":list_data.get(item)[2].sale,
                               "date_create":list_data.get(item)[0],
                               "price_off":list_data.get(item)[2].price_off* list_data.get(item)[1],
                               "shopify_report":self.id,
                           })
                       else:
                           find_bundle_data.create({
                               "bundle_id": list_data.get(item)[2].discount_id.id,
                               "discount_id": list_data.get(item)[2].id,
                               "number_add_to_cart": list_data.get(item)[1],
                               "sale": list_data.get(item)[2].sale,
                               "date_create": list_data.get(item)[0],
                               "price_off": list_data.get(item)[2].price_off,
                               "shopify_report": self.id,
                           })
                   self.flag = True
       else:
           find_bundle_data = request.env['shopify.discount.count']
           find_bundle_data.unlink()









class SAppDiscountDataCount(models.Model):
    _name = 'shopify.discount.count'
    discount_id = fields.Many2one('shopify.discount.data')
    bundle_id = fields.Many2one('shopify.discount')
    number_add_to_cart = fields.Integer(string='Total number add to cart')
    sale = fields.Char(string='Sale Amount')
    date_create = fields.Datetime(string="Date Created")
    # total_revenue = fields.Float(string="Total Revenue")
    price_off = fields.Float(string="Price Off")
    shopify_report = fields.Many2one('shopify.discount.report')





