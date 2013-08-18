"""
Unit tests for the Account class.
"""

import unittest
import httpretty
from mock import MagicMock

from swiftest.account import Account

class TestAccount(unittest.TestCase):

    def setUp(self):
        httpretty.enable()

        self.client = MagicMock(name='Client')
        self.client.auth_token = '12345'
        self.client.storage_url = 'http://storage.example.com/v1/account'

    def test_account_metadata(self):
        httpretty.register_uri(httpretty.HEAD, 'http://storage.example.com/v1/account', status=204,
            x_account_container_count=123, x_account_bytes_used=102400)

        a = Account(self.client)
        self.assertEquals(123, a.container_count)
        self.assertEquals(102400, a.bytes_used)

    def tearDown(self):
        httpretty.disable()
