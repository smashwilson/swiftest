"""
Unit tests for the SwiftestObject class.
"""

import unittest
import httpretty

from io import BytesIO

from swiftest.swiftest_object import SwiftestObject
from httpretty import GET, PUT

from . import util

class SwiftestObjectTest(unittest.TestCase):

    def setUp(self):
        httpretty.enable()
        self.client = util.create_client()

    def test_download_binary(self):
        httpretty.register_uri(GET, util.STORAGE_URL + '/contname/objectname',
            status=200, body='object content')

        o = SwiftestObject(self.client, 'contname', 'objectname')

        self.assertEqual(o.download_binary(), b'object content')

    def test_download_string(self):
        httpretty.register_uri(GET, util.STORAGE_URL + '/contname/objectname',
            status=200, body='object content')

        o = SwiftestObject(self.client, 'contname', 'objectname')

        string = o.download_string(encoding='utf-8')
        self.assertEqual(string, u'object content')

    def test_download_file(self):
        httpretty.register_uri(GET, util.STORAGE_URL + '/contname/objectname',
            status=200, body='object content')

        o = SwiftestObject(self.client, 'contname', 'objectname')

        dest = BytesIO()
        o.download_file(dest)
        self.assertEqual(dest.getvalue(), b'object content')
        dest.close()

    def tearDown(self):
        httpretty.disable()
