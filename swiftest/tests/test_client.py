"""
Unit tests for the Client class.
"""

import unittest
import httpretty

from swiftest.client import Client
from swiftest.exception import AuthenticationError

class TestClient(unittest.TestCase):

    def setUp(self):
        httpretty.enable()

    def test_authenticate_successfully(self):
        """
        Creating a client object immediately authenticates.
        """

        httpretty.register_uri(httpretty.GET, 'http://auth.endpoint.com/v1/', status=204,
            x_auth_token='12345abcdef',
            x_storage_url='http://storage.endpoint.com/v1/account')

        client = Client(endpoint='http://auth.endpoint.com/v1/',
            username='me', auth_key='swordfish')

        auth_req_headers = httpretty.last_request().headers
        self.assertEqual(auth_req_headers['X-Auth-User'], 'me')
        self.assertEqual(auth_req_headers['X-Auth-Key'], 'swordfish')

        self.assertEqual(client.auth_token, '12345abcdef')
        self.assertEqual(client.storage_url, 'http://storage.endpoint.com/v1/account')

    def test_authentication_failure(self):
        """
        Raise an exception if authentication fails.
        """

        httpretty.register_uri(httpretty.GET, 'http://auth.endpoint.com/v1/', status=401)

        try:
            Client(endpoint='http://auth.endpoint.com/v1/',
                username='me', auth_key='bad')
            self.fail('Did not raise an error with bad credentials')
        except AuthenticationError:
            pass

    def tearDown(self):
        httpretty.disable()
