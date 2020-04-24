import time
import os
import json
import logging

import zeep
import zeep.cache
import requests

# ************************************************************************************************
# SETUP 
# ************************************************************************************************

log = logging.getLogger(__name__)

session = requests.Session()
transport = zeep.Transport(cache = zeep.cache.InMemoryCache(), session = session)

# *************************************************************************************************
# CLASSES
# *************************************************************************************************

class TokenManager():
    """Manages SOAP API tokens for Planon

    """

    token_default_expires = 28800

    def __init__(self, url, username, password, token_age_threshold=900):
        self.url = url
        self.username = username
        self._password = password
        self.token_age_threshold = token_age_threshold

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

            try:
                token = self.session_client.service.login(self.username, self._password)

                self.token_wrapper['token'] = token
                self.token_wrapper['expires'] = time.time() + self.token_default_expires
            except zeep.exceptions.Fault as e:
                if e.message == 'unknown':
                    log.error('Planon session SOAP API "unknown" errors are typically due to invalid passwords')
                    raise e

            return self.token_wrapper['token']