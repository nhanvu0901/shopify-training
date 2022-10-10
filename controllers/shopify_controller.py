import json
from odoo import http
from odoo.http import request
import hmac
import hashlib
import requests
import werkzeug
import os
import jinja2
from pytz import timezone
from datetime import datetime


path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../static/src/html'))
loader = jinja2.FileSystemLoader(path)
jinja_env = jinja2.Environment(loader=loader, autoescape=True)
jinja_env.filters["json"] = json.dumps



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



class SShopify(http.Controller):

    @http.route('/shopify', auth='user')
    def sc_index(self, **kw):
        template = jinja_env.get_template('index.html')
        res = template.render()
        return res

    @http.route('/shopify/install_app', type="http", auth="public", website=True, method=['GET'], csrf=False)
    def install_app(self, **kwargs):
        print(kwargs)
        shop_url = kwargs['shop']
        api_key = request.env['ir.config_parameter'].sudo().get_param('shopify.api_key')
        state = kwargs['hmac']
        callback = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/shopify/oauth/callback'

        url = f"https://{shop_url}/admin/oauth/authorize?client_id={api_key}&scope={SCOPES}&redirect_uri={callback}&state={state}&grant_options[]=per-user"
        return werkzeug.utils.redirect(url)