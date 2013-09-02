"""
Download and upload individual OpenStack Swift objects.
"""

import requests
import shutil

class SwiftestObject:
    """
    A single object stored within a Container.

    SwiftestObjects may represent a named object already uploaded to OpenStack
    Swift, or a potential object that can be uploaded with one of the "upload_"
    methods.
    """

    def __init__(self, client, container_name, name):
        self.client = client
        self.container_name = container_name
        self.name = name

    def download_string(self, encoding=None):
        """
        Download the contents as a String.

        By default, the String's encoding will be inferred from header
        information by the underlying requests call, overridden by an
        explicit encoding if one is provided.
        """

        resp = self._content_resp()
        if encoding:
            resp.encoding = encoding
        return resp.text

    def download_binary(self):
        """
        Download this object's content as uninterpreted binary.
        """

        return self._content_resp().content

    def download_file(self, io, buffer_size=None):
        """
        Download the contents of a named object to an open file-like destination.

        Provide a custom buffer size to override the default copy buffer provided by shutils. Be sure
        that "io" is opened in binary mode if this object contains binary data, to avoid newline
        translation or other encoding hiccups.

        Opening and closing "io" is the caller's responsibility.
        """

        resp = self._content_resp(stream=True)
        shutil.copyfileobj(resp.raw, io, buffer_size)

    def _content_resp(self, **kwargs):
        return self.client._call(requests.get,
            '/{0}/{1}'.format(self.container_name, self.name),
            **kwargs)
