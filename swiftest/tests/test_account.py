"""
Unit tests for the Account class.
"""

import unittest
import requests
import httpretty
from httpretty import HEAD, POST

from swiftest.client import Client
from swiftest.account import Account

from . import util
from .util import create_client

class AccountTest(unittest.TestCase):

    def setUp(self):
        httpretty.enable()
        self.client = create_client()

    def test_account_metadata(self):
        """
        Creating an Account reads metadata from HTTP headers.
        """

        httpretty.register_uri(HEAD, util.STORAGE_URL, status=204,
            x_account_container_count=123, x_account_bytes_used=102400)

        a = Account(self.client)
        self.assertEqual(123, a.container_count)
        self.assertEqual(102400, a.bytes_used)

    def test_account_auth_failure(self):
        """
        An error is raised if the token is rejected.
        """

        httpretty.register_uri(HEAD, util.STORAGE_URL, status=401)

        try:
            Account(self.client)
            self.fail('Did not fail on a rejected token.')
        except requests.HTTPError:
            pass

    def test_report_metadata(self):
        """
        The metadata property is populated with any account metadata.
        """

        httpretty.register_uri(HEAD, util.STORAGE_URL, status=204,
            x_account_container_count=0, x_account_bytes_used=0,
            x_account_meta_one='something', x_account_meta_two='else')

        a = Account(self.client)
        self.assertEqual('something', a.metadata['one'])
        self.assertEqual('else', a.metadata['two'])

    def test_create_metadata(self):
        """
        Account metadata can be added through the metadata property.
        """

        httpretty.register_uri(HEAD, util.STORAGE_URL, status=200,
            x_account_container_count=0, x_account_bytes_used=0)
        httpretty.register_uri(POST, util.STORAGE_URL, status=200)

        a = Account(self.client)
        a.metadata['foo'] = 'some-value'
        a.metadata['bar'] = 'another-value'
        a.metadata.save()

        headers = httpretty.last_request().headers
        self.assertEqual('some-value', headers['X-Account-Meta-Foo'])
        self.assertEqual('another-value', headers['X-Account-Meta-Bar'])

    def test_delete_metadata(self):
        """
        Account metadata can be deleted by manipulating the metadata property.
        """

        httpretty.register_uri(HEAD, util.STORAGE_URL, status=200,
            x_account_container_count=0, x_account_bytes_used=0,
            x_account_meta_one='something')
        httpretty.register_uri(POST, util.STORAGE_URL, status=200)

        a = Account(self.client)
        del a.metadata['one']
        a.metadata.save()

        headers = httpretty.last_request().headers
        self.assertEqual('', headers['X-Account-Meta-One'])

    def tearDown(self):
        httpretty.disable()
