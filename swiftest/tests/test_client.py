"""
Unit tests for the Client class.
"""

import unittest
import httpretty

from swiftest.client import Client

class TestClient(unittest.TestCase):

    def setUp(self):
        httpretty.enable()

    def test_authenticate_successfully(self):
        """
        Creating a client object immediately authenticates.
        """

        httpretty.register_uri(httpretty.GET, 'http://auth.endpoint.com/v1/', status=204,
            x_auth_token='12345abcdef',
            x_storage_url='http://storage.endpoint.com/v1/')

        client = Client(endpoint='http://auth.endpoint.com/v1/',
            username='me', auth_key='swordfish')

        auth_req_headers = httpretty.last_request().headers
        self.assertEqual(auth_req_headers['X-Auth-User'], 'me')
        self.assertEqual(auth_req_headers['X-Auth-Key'], 'swordfish')

        self.assertEqual(client.auth_token, '12345abcdef')
        self.assertEqual(client.storage_url, 'http://storage.endpoint.com/v1/')

    def tearDown(self):
        httpretty.disable()
