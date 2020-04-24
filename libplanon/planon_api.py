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




def token_provider(
    username=os.environ['PLN_USR'], 
    password=os.environ['PLN_PWD'], 
    url=os.environ['PLN_URL'], 
    token_age_threshold=300,
    default_token_age=400):
    """
    Closure function to generate tokens and persist valid tokens in memory.

    Keyword arguments:
    username -- username
    password -- password
    url -- URL to request a token
    """

    # TODO verify all parameters simultaneously?
    if not username: raise ValueError('Username must be specified')
    if not password: raise ValueError('Password must be specified')
    if not password: raise ValueError('URL must be specified')

    log.debug('Initializaing zeep client')
    token_client = zeep.Client(wsdl=f'{url}/PlanonSession?wsdl', transport=transport)

    # Provides persistent token storage
    self.token_wrapper = {
        'issued': None,
        'token': None
    }

    def get_token():
        # Allows the token to be updated if needed
        nonlocal self.token_wrapper

        log.debug(f"Current token: [ {self.token_wrapper.get('token','')} ]")

        if self.token_wrapper['issued'] and self.token_wrapper['issued'] - time.time() > token_age_threshold:
            log.debug('Existing token is within age threshold, returning.')
            return self.token_wrapper['token']

        log.info('Requesting new token.')
        self.token_wrapper['token'] = token_client.service.login(username, password)

        self.token_wrapper['issued'] = time.time() + default_token_age

        return self.token_wrapper['token']

    # This closure returns the inner function, this allows persistent storage of the JWT and for the JWT to be refreshed when expiring
    return get_token