# -*- coding: UTF-8 -*-

try:
    from ConfigParser import SafeConfigParser
except ImportError:  # Python 3
    from configparser import SafeConfigParser

from os import chmod
from os.path import expanduser, isfile


class DidelConfig(object):
    """
    A wrapper for Python's ConfigParser which uses paths instead of sections

    >>> config = DidelConfig("foo.conf")
    >>> config.set("foo", 45)
    >>> config.get("foo")
    "45"
    >>> config.set("stuff.bar", "hello")
    >>> config.get("stuff.bor")
    None
    >>> config.get("stuff.bar")
    "hello"
    """

    SOURCE_FILE = expanduser('~/.didel.conf')
    _default = None

    @classmethod
    def get_default(cls):
        """
        Get the default config object.
        """
        if not cls._default:
            cls._default = cls()
        return cls._default


    def __init__(self, filename=SOURCE_FILE):
        self.filename = filename
        self.config = SafeConfigParser()
        if not isfile(self.filename):
            self.save()
        self.load()


    def load(self):
        self.config.read(self.filename)


    def save(self):
        with open(self.filename, 'w') as f:
            self.config.write(f)
        chmod(self.filename, 0600)


    def _split_path(self, key):
        """
        Split a key into a ``(section, key)`` tuple.
        """
        return key.split('.', 1) if '.' in key else ('DEFAULT', key)


    def set(self, key, value):
        """
        Set a value. It creates the section if it doesn't exist

        >>> config.set("foo.bar", 42)
        """
        section, key = self._split_path(key)
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        return self


    def get(self, key):
        """
        Get a value. It returns ``None`` if it doesn't exist.

        >>> config.get("foo.bar")
        "42"
        """
        section, key = self._split_path(key)
        if not self.config.has_section(section) or section == 'secret':
            return None
        return self.config.get(section, key)


    def items(self):
        """
        Yield all items from this config, as tuples of ``(key, value)``
        """
        for section in self.config.sections():
            if section == 'secret':
                continue
            for k, v in self.config.items(section):
                yield ('%s.%s' % (section, k), v)


    def __del__(self):
        self.save()
