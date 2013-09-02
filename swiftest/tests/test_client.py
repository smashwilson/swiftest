"""
Unit tests for the Client class.
"""

import unittest
import httpretty
import requests

from httpretty import GET, HEAD
from swiftest.client import Client

from . import util

class ClientTest(unittest.TestCase):

    def setUp(self):
        httpretty.enable()

    def create_client(self):
        """
        Utility method to create an authenticated Client.
        """
        httpretty.register_uri(GET, 'http://auth.endpoint.com/v1/', status=204,
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
        httpretty.register_uri(GET, 'http://storage.endpoint.com/v1/account', status=200,
            body=container_list)

        client = self.create_client()
        self.assertEqual(['foo', 'bar', 'baz'], client.container_names())

    def test_container_generator(self):
        """
        The containers() method generates Container objects.
        """

        container_list = "foo\nbar\nbaz"
        httpretty.register_uri(GET, 'http://storage.endpoint.com/v1/account', status=200,
            body=container_list)
        httpretty.register_uri(HEAD, 'http://storage.endpoint.com/v1/account/foo', status=204,
            x_container_object_count=0, x_container_bytes_used=0)
        httpretty.register_uri(HEAD, 'http://storage.endpoint.com/v1/account/bar', status=204,
            x_container_object_count=0, x_container_bytes_used=0)
        httpretty.register_uri(HEAD, 'http://storage.endpoint.com/v1/account/baz', status=204,
            x_container_object_count=0, x_container_bytes_used=0)

        client = self.create_client()
        names = [cont.name for cont in client.containers()]
        self.assertEqual(['foo', 'bar', 'baz'], names)

    def test_get_container_by_name(self):
        """
        Get a Container within this account by its name.
        """

        httpretty.register_uri(HEAD, 'http://storage.endpoint.com/v1/account/contname', status=204,
            x_container_object_count=0, x_container_bytes_used=0)

        client = self.create_client()
        container = client.container('contname')
        self.assertTrue(container.exists())

    def tearDown(self):
        httpretty.disable()
