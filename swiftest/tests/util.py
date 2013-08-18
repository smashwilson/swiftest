"""
Unit testing utility functions.
"""

import httpretty

from swiftest.client import Client

def create_client():
    """
    Mock the authentication endpoint to create a Client object.

    Assumes that httpretty is already enabled.
    """

    httpretty.register_uri(httpretty.GET, 'http://auth.endpoint.com/v1/', status=204,
        x_auth_token='12345abcdef',
        x_storage_url='http://storage.endpoint.com/v1/account')

    return Client(endpoint='http://auth.endpoint.com/v1/',
        username='me', auth_key='swordfish')
