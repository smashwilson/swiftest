"""
Unit tests for the Container and NullContainer classes.
"""

import unittest
import httpretty

from httpretty import GET, PUT, POST, HEAD, DELETE

from swiftest.container import Container, NullContainer
from swiftest.client import Client
from swiftest.exception import AlreadyExistsError
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

    def test_null_container(self):
        c = NullContainer(self.client, 'nothere')
        self.assertFalse(c.exists())

    def test_create_new(self):
        httpretty.register_uri(PUT, util.STORAGE_URL + '/notyet', status=201)
        httpretty.register_uri(HEAD, util.STORAGE_URL + '/notyet', status=204,
            x_container_object_count=0, x_container_bytes_used=0)

        c = NullContainer(self.client, 'notyet')
        created = c.create()

        self.assertEqual('notyet', created.name)
        self.assertEqual(self.client, created.client)

    def test_create_existing(self):
        httpretty.register_uri(HEAD, util.STORAGE_URL + '/contname', status=204,
            x_container_object_count=1234, x_container_bytes_used=102400)
        c = Container(self.client, 'contname')

        try:
            c.create()
            self.fail("Did not raise on creation of already existing container")
        except AlreadyExistsError:
            pass

    def test_create_if_necessary_noop(self):
        httpretty.register_uri(HEAD, util.STORAGE_URL + '/contname', status=204,
            x_container_object_count=1234, x_container_bytes_used=102400)
        c = Container(self.client, 'contname')

        self.assertEqual(c, c.create_if_necessary())

    def test_download_binary(self):
        httpretty.register_uri(GET, util.STORAGE_URL + '/contname/objectname',
            status=200, body='object content')
        c = Container(self.client, 'contname')

        binary = c.download_binary('objectname')
        self.assertEqual(binary, b'object content')

    def test_download_string(self):
        httpretty.register_uri(GET, util.STORAGE_URL + '/contname/objectname',
            status=200, body='object content')
        c = Container(self.client, 'contname')

        string = c.download_string('objectname', encoding='utf-8')
        self.assertEqual(string, u'object content')

    def test_delete_container(self):
        httpretty.register_uri(DELETE, util.STORAGE_URL + '/contname', status=204)
        c = Container(self.client, 'contname')
        c.delete()

    def tearDown(self):
        httpretty.disable()
