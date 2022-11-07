# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import shopify

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shop_url = fields.Char(string='Shop URL', config_parameter="test_shopi.shop_url")
    api_version = fields.Char(string='Api version', config_parameter="test_shopi.api_version")
    redirect_url = fields.Char(string="Redirect URL", config_parameter="test_shopi.redirect_url")
    sp_api_key = fields.Char(string='API Key', config_parameter="test_shopi.sp_api_key")
    sp_api_secret_key = fields.Char(string='API secret key', config_parameter="test_shopi.sp_api_secret_key")
    cdn_tag = fields.Char(string='CDN tag', config_parameter="test_shopi.cdn_tag")


    #xero acounting
    client_id = fields.Char(string="Client ID",config_parameter="test_shopi.client_id")
    client_secret = fields.Char(string="Client Secret",config_parameter="test_shopi.client_secret")
    redirect_url_xero = fields.Char(string="Redirect URL",config_parameter="test_shopi.redirect_url_xero")
