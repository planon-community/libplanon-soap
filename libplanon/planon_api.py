import time
import os
import base64
import json
import logging
import urllib

import zeep
import zeep.cache
import requests

# ************************************************************************************************
# SETUP 
# ************************************************************************************************

log = logging.getLogger(__name__)

services = ['Department', 'PlanonSession']

# urllib seems to drop the trailing resource if there is no trailing slash
pln_url = os.environ.get('PLN_URL') if os.environ.get('PLN_URL')[-1] == '/' else f"{os.environ.get('PLN_URL')}/"

log = logging.getLogger(__name__)

session = requests.Session()
transport = zeep.Transport(cache = zeep.cache.InMemoryCache(), session = session)

# *************************************************************************************************
# FUNCTIONS
# *************************************************************************************************

class TokenManager():
    """Manages SOAP API tokens for Planon

    """

    token_default_expires = 28800

    def __init__(self, url=os.environ.get('PLN_URL'), username=os.environ.get('PLN_USR'), password=os.environ.get('PLN_PWD'), token_age_threshold=900):
        self.url = url
        self.username = username
        self._password = password
        self._token_age_threshold = token_age_threshold

        self.token_wrapper = {
            'expires': None,
            'token': None
        }

        self.session_client = zeep.Client(wsdl=f'{self.url}/PlanonSession?wsdl', transport=transport)

    def get_token(self):
        if self.token_wrapper['expires'] and self.token_wrapper['expires'] - time.time() > self.token_age_threshold:
            log.debug('Existing token is within age threshold, returning.')
            return self.token_wrapper['token']
        else:
            log.info('Requesting new token.')

            self.token_wrapper['token'] = self.session_client.service.login(self.username, self.password)
            self.token_wrapper['expires'] = time.time() + token_default_expires

            return self.token_wrapper['token']