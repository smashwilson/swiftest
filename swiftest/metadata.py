import re

class Metadata(dict):
    """
    Provide dict-like access to account metadata.

    save() must be called to commit any changes.
    """

    def __init__(self, parent, existing):
        dict.__init__(self, existing)
        self.parent = parent
        self.updates = []
        self.deletions = []

    def save(self):
        """
        Invoke the _commit_metadata() callback on the parent object.
        """
        self.parent._commit_metadata(self)

    def __setitem__(self, key, value):
        """
        Record the addition or update of a value.
        """

        if key not in self or self[key] != value:
            self.updates.append(key)
        dict.__setitem__(self, key, value)

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

        return cls(parent, existing)
