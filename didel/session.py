# -*- coding: UTF-8 -*-

from cookielib import LWPCookieJar
from os.path import expanduser, isfile
from requests import Session as BaseSession

COOKIES_FILE = expanduser('~/.didel.cookies')


class Session(BaseSession):
    """
    A session with persistent cookies storage
    """

    def __init__(self, *args, **kwargs):
        """
        Same constructor as parent class except that if ``cookies_file`` is
        given it'll override the default cookies file.
        """
        k = 'cookies_file'
        cookies_file = kwargs.pop(k) if k in kwargs else COOKIES_FILE
        super(Session, self).__init__(*args, **kwargs)
        self.cookies_file = k
        self.cookies = LWPCookieJar(cookies_file)
        self.load()

    def save(self):
        """
        Save the session
        """
        if self.cookies_file is not None:
            self.cookies.save()

    def load(self):
        """
        Load a previously saved session
        """
        if isfile(self.cookies_file):
            self.cookies.load()

    def __del__(self):
        self.save()
