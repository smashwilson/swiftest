"""
Unit tests for the Client class.
"""

import unittest
import httpretty
import requests

from swiftest.client import Client

class TestClient(unittest.TestCase):

    def setUp(self):
        httpretty.enable()

    def create_client(self):
        """
        Utility method to create an authenticated Client.
        """
        httpretty.register_uri(httpretty.GET, 'http://auth.endpoint.com/v1/', status=204,
            x_auth_token='12345abcdef',
            x_storage_url='http://storage.endpoint.com/v1/account')

        return Client(endpoint='http://auth.endpoint.com/v1/',
            username='me', auth_key='swordfish')

    def test_authenticate_successfully(self):
        """
        Creating a client object immediately authenticates.
        """

        client = self.create_client()
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
        except requests.HTTPError:
            pass

    def test_list_container_names(self):
        """
        List all container names present in an account.
        """

        container_list = "foo\nbar\nbaz"
        httpretty.register_uri(httpretty.GET, 'http://storage.endpoint.com/v1/account', status=200,
            body=container_list)

        client = self.create_client()
        self.assertEqual(['foo', 'bar', 'baz'], client.container_names())

    def tearDown(self):
        httpretty.disable()
