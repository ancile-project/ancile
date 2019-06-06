class PrivateData(object):
    """
    Wrapper object that represents data to be substituted in.

    The object stores a keyword. When a PrivateData object is used as a
    parameter to an ancile fn, the key is used to substitute a value from the
    user's private data store.
    """
    def __init__(self, key=None):
        """
        :param str key: The key held by the object. May be none.
        """
        self._key = key

    def __eq__(self, other):
        """Equality check. Used during policy checks."""
        if self is other:
            return True
        elif isinstance(other, self.__class__):
            return self._key == other._key
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f'<PrivateData. {self._key}>'

