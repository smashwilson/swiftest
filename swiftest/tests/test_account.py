"""
Unit tests for the Account class.
"""

import unittest
import httpretty
import requests

from swiftest.client import Client
from swiftest.account import Account

class TestAccount(unittest.TestCase):

    def setUp(self):
        httpretty.enable()

        # Mock the authentication endpoint to create a real Client.
        httpretty.register_uri(httpretty.GET, 'http://auth.endpoint.com/v1/', status=204,
            x_auth_token='12345abcdef',
            x_storage_url='http://storage.endpoint.com/v1/account')

        self.client = Client(endpoint='http://auth.endpoint.com/v1/',
            username='me', auth_key='swordfish')

    def test_account_metadata(self):
        """
        Creating an Account reads metadata from HTTP headers.
        """
        httpretty.register_uri(httpretty.HEAD, 'http://storage.endpoint.com/v1/account', status=204,
            x_account_container_count=123, x_account_bytes_used=102400)

        a = Account(self.client)
        self.assertEquals(123, a.container_count)
        self.assertEquals(102400, a.bytes_used)

    def test_account_auth_failure(self):
        """
        An error is raised if the token is rejected.
        """

        httpretty.register_uri(httpretty.HEAD, 'http://storage.endpoint.com/v1/account', status=401)

        try:
            Account(self.client)
            self.fail('Did not fail on a rejected token.')
        except requests.HTTPError:
            pass

    def tearDown(self):
        httpretty.disable()
