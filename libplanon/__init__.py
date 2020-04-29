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
    Args:
        url (str):
        username (str):
        password (str):
        reference_date (str): '2020-01-01T00:00:00'
    Returns
        TokenManager
    """

    token_default_expires = 28800

    def __init__(self, url, username, password, reference_date=None, token_age_threshold=900):
        self.url = url
        self.username = username
        self._password = password
        self.token_age_threshold = token_age_threshold
        self.reference_date = reference_date

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

            if self.reference_date:
                log.debug(f'Setting token reference date to {self.reference_date}')
                result = self.session_client.service.setReferenceDate(token, self.reference_date)

            else:
                log.debug('Disabling reference date')
                result = self.session_client.service.setReferenceDate(token, None)

            return self.token_wrapper['token']


class APIManager(object):

    def _get_clients(self, services):
        for service in services:
            self._clients.update({service: zeep.Client(wsdl=f'{self.url}/{service}?wsdl', transport=transport).service})

    def __init__(self, url, services):
        self.url = url
        self.services = services

        self._clients = {}

        self._get_clients(services=services)

    def __getitem__(self, item):
        return self._clients[item]