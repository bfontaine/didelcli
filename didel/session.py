# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from cookielib import LWPCookieJar
from os.path import expanduser, isfile
from requests import Session as BaseSession

COOKIES_FILE = expanduser('~/.didel.cookies')

URLS = {
    'login': 'https://auth.univ-paris-diderot.fr/cas/login',
    'logout': 'https://auth.univ-paris-diderot.fr/cas/logout',
}

class Session(BaseSession):
    """
    A session with persistent cookies storage and builtin authentification
    support for Paris Diderot's websites.
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

    def login(self, username, passwd):
        """
        Authenticate an user
        """
        url = URLS['login']
        soup = BeautifulSoup(self.get(url).text)
        lts = soup.select('input[name=lt]')
        if not lts:
            return False
        formkey = lts[0].attrs['value']
        resp = self.post(url, {
            'username': username,
            'password': passwd,
            'lt': formkey,
            '_eventId': 'submit',
        })
        return resp.ok and 'Log In Successful' in resp.text

    def logout(self):
        return 'Logout successful' in self.get(URLS['logout']).text

    def __del__(self):
        self.save()
