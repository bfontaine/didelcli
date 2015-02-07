# -*- coding: UTF-8 -*-

try:
    from ConfigParser import SafeConfigParser
except ImportError:  # Python 3
    from configparser import SafeConfigParser

import base64
from os import chmod
from os.path import expanduser, isfile


class DidelConfig(object):
    """
    A wrapper for Python's ConfigParser which uses paths instead of sections

    It must be saved with ``.save()`` to be persistent.

    >>> config = DidelConfig("foo.conf")
    >>> config.set("foo", 45)
    >>> config.get("foo")
    "45"
    >>> config.set("stuff.bar", "hello")
    >>> config.get("stuff.bor")
    None
    >>> config.get("stuff.bar")
    "hello"
    >>> config.save()
    """

    SOURCE_FILE = expanduser('~/.didel.conf')
    SECRET_SECTION = 'secret'
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
        # octal numbers are written as '0600' in Python2 and '0o600' in Python3
        # to avoid any problem we're writing the permissions as a decimal
        # number here
        chmod(self.filename, 384)


    def _split_path(self, key):
        """
        Split a key into a ``(section, key)`` tuple.
        """
        return key.split('.', 1) if '.' in key else ('DEFAULT', key)


    def set(self, key, value, save=False):
        """
        Set a value. It creates the section if it doesn't exist

        >>> config.set("foo.bar", "42")
        """
        section, key = self._split_path(key)
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        if save:
            self.save()
        return self


    def get(self, key, default=None):
        """
        Get a value. It returns ``default`` if it doesn't exist.

        >>> config.get("foo.bar")
        "42"
        >>> config.get("dontexist")
        None
        >>> config.get("dontexist", "foo")
        "foo"
        """
        if not self.has_key(key):
            return default
        section, key = self._split_path(key)
        return self.config.get(section, key)


    def has_key(self, key):
        """
        Test if a key exist
        """
        section, key = self._split_path(key)
        cfg = self.config
        return cfg.has_section(section) and cfg.has_option(section, key)


    def set_secret(self, key, value, save=False):
        """
        Same as ``set`` but use a simple encryption. If no section is
        specified, it uses the secret one.
        """
        if '.' not in key:
            key = '%s.%s' % (self.SECRET_SECTION, key)
        return self.set(key, base64.b16encode(value), save)


    def get_secret(self, key):
        """
        Same as ``get`` but use a simple encryption. If no section is
        specified, it uses the secret one.
        """
        if '.' not in key:
            key = '%s.%s' % (self.SECRET_SECTION, key)
        value = self.get(key)
        if value is not None:
            return base64.b16decode(value)


    def has_secret_key(self, key):
        """
        Same as ``has_key`` but for the secret section
        """
        if '.' not in key:
            key = '%s.%s' % (self.SECRET_SECTION, key)
        return self.has_key(key)


    def get_credentials(self):
        """
        Return a pair of "username" and "password" keys. This is roughly the
        same as the following code: ::

            (cfg.get_secret('username'), cfg.get_secret('password'))

        Except that it can try various fallbacks if one of them is ``None``
        (i.e. the credentials weren't properly configured).
        """
        username = self.get_secret('username')
        passwd = self.get_secret('password')
        if username is None or passwd is None:
            return self._get_netrc_credentials()
        return (username, passwd)


    def _get_netrc_credentials(self, filename=None):
        """
        Fallback of ``get_credentials`` if credentials weren't configured. It
        tries to find credentials in the user's ``~/.netrc`` file.
        """
        from netrc import NetrcParseError, netrc as NetrcFile
        source = None
        try:
            source = NetrcFile(filename)
        except NetrcParseError:
            return (None, None)

        hosts = [
            'didel.script.univ-paris-diderot.fr',
            'auth.univ-paris-diderot.fr',
            'univ-paris-diderot.fr',
        ]

        for host in hosts:
            res = source.authenticators(host)
            if res:
                login, _, password = res
                return (login, password)

        return (None, None)


    def items(self):
        """
        Yield all items from this config, as tuples of ``(key, value)``
        """
        for section in self.config.sections():
            if section == self.SECRET_SECTION:
                continue
            for k, v in self.config.items(section):
                yield ('%s.%s' % (section, k), v)
