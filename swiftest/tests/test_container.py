"""
Unit tests for the Container and NullContainer classes.
"""

import unittest
import httpretty

from httpretty import GET, PUT, POST, HEAD

from swiftest.container import Container
from swiftest.client import Client
from . import util

class TestContainer(unittest.TestCase):

    def setUp(self):
        httpretty.enable()
        self.client = util.create_client()

    def test_get_container_metadata(self):
        httpretty.register_uri(HEAD, util.STORAGE_URL + '/contname', status=204,
            x_container_object_count=1234, x_container_bytes_used=102400, x_container_meta_meta1='a value')

        c = Container(self.client, 'contname')
        self.assertTrue(c.exists())
        self.assertEqual(1234, c.object_count)
        self.assertEqual(102400, c.bytes_used)
        self.assertEqual('a value', c.metadata['meta1'])

    def test_update_container_metadata(self):
        httpretty.register_uri(HEAD, util.STORAGE_URL + '/contname', status=204,
            x_container_object_count=1234, x_container_bytes_used=102400, x_container_meta_meta1='a value')
        httpretty.register_uri(POST, util.STORAGE_URL + '/contname', status=200)

        c = Container(self.client, 'contname')
        c.metadata['meta2'] = 'another value'
        c.metadata.save()

        hs = httpretty.last_request().headers
        self.assertEqual('another value', hs['X-Container-Meta-Meta2'])

    def test_delete_container_metadata(self):
        httpretty.register_uri(HEAD, util.STORAGE_URL + '/contname', status=204,
            x_container_object_count=1234, x_container_bytes_used=102400, x_container_meta_meta1='a value')
        httpretty.register_uri(POST, util.STORAGE_URL + '/contname', status=200)

        c = Container(self.client, 'contname')
        del c.metadata['meta1']
        c.metadata.save()

        hs = httpretty.last_request().headers
        self.assertEqual('', hs['X-Container-Meta-Meta1'])

    def tearDown(self):
        httpretty.disable()
