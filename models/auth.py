import json
import os
import shopify
from xero import Xero
from xero.auth import OAuth2Credentials
from xero.constants import XeroScopes
import logging

local_session = None
local_env = None
_logger = logging.getLogger(__name__)

class XeroAuth(OAuth2Credentials):
    def __init__(
            self,
            client_id=None,
            client_secret=None,
            callback_uri=None,
            auth_state=None,
            auth_secret=None,
            token=None,
            scope=None,
            tenant_id=None,
            user_agent=None,
    ):
        if user_agent is None:
            user_agent = 'Magenest/1.0.0'
        if scope is None:
            scope = [
                XeroScopes.OFFLINE_ACCESS,
                XeroScopes.ACCOUNTING_CONTACTS_READ,
                XeroScopes.ACCOUNTING_CONTACTS,
                XeroScopes.ACCOUNTING_TRANSACTIONS_READ,
                XeroScopes.ACCOUNTING_TRANSACTIONS,
                XeroScopes.ACCOUNTING_SETTINGS_READ,
                XeroScopes.ACCOUNTING_SETTINGS
            ]
        super(XeroAuth, self).__init__(
            client_id,
            client_secret,
            callback_uri,
            auth_state,
            auth_secret,
            token,
            scope,
            tenant_id,
            user_agent
        )

    def verify(self, *args, **kwargs):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        super(XeroAuth, self).verify(*args, **kwargs)
        os.environ.pop('OAUTHLIB_INSECURE_TRANSPORT')