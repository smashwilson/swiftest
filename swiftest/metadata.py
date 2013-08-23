import re
import requests

class Metadata(dict):
    """
    Provide dict-like access to account metadata.

    save() must be called to commit any changes.
    """

    def __init__(self, parent, prefix, existing):
        dict.__init__(self, existing)
        self.parent = parent
        self.prefix = prefix
        self.updates = set()
        self.deletions = set()

    def save(self):
        """
        Create, update or delete metadata in the parent object based on the changes
        made to this dictionary.
        """

        h = {}
        for update in self.updates:
            h["X-{0}-Meta-{1}".format(self.prefix, update)] = self[update]
        for deletion in self.deletions:
            h["X-{0}-Meta-{1}".format(self.prefix, deletion)] = ''
        self.parent.client._call(requests.post, '', headers=h)

    def __setitem__(self, key, value):
        """
        Record the addition or update of a value.
        """

        lkey = key.lower()
        if lkey not in self or self[lkey] != value:
            self.updates.add(lkey)
        if value and lkey in self.deletions:
            self.deletions.remove(lkey)
        dict.__setitem__(self, lkey, value)

    def __delitem__(self, key):
        """
        Record the deletion of a value.
        """

        lkey = key.lower()
        dict.__delitem__(self, lkey)
        self.deletions.add(lkey)
        if key in self.updates:
            self.updates.remove(lkey)

    @classmethod
    def from_response(cls, parent, response, prefix):
        """
        Populate Metadata from a GET or HEAD response.
        """

        existing = {}
        meta = re.compile("X-{0}-Meta-(.+)".format(prefix), re.IGNORECASE)
        for (header, value) in response.headers.items():
            match = meta.match(header)
            if match:
                existing[match.group(1).lower()] = value

        return cls(parent, prefix, existing)
