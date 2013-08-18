"""
Unit tests for the Account class.
"""

import unittest
import httpretty
import requests

from swiftest.client import Client
from swiftest.account import Account

from .util import create_client

class TestAccount(unittest.TestCase):

    def setUp(self):
        httpretty.enable()
        self.client = create_client()

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
