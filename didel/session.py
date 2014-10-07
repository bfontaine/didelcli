# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from cookielib import LWPCookieJar
from os.path import expanduser, isfile
from requests import Session as BaseSession

from didel.base import ROOT_URL

URLS = {
    'login': 'https://auth.univ-paris-diderot.fr/cas/login',
    'logout': 'https://auth.univ-paris-diderot.fr/cas/logout',

    'login_service':
        'http://didel.script.univ-paris-diderot.fr/claroline/auth/login.php' \
        '?authModeReq=CAS',
}

DEFAULTS = {
    'cookies_file': expanduser('~/.didel.cookies'),
    'user_agent': 'Python/DidelCli +b@ptistefontaine.fr',
}


class Session(BaseSession):
    """
    A session with persistent cookies storage and builtin authentification
    support for Paris Diderot's websites as well as custom default headers.
    """

    def __init__(self, *args, **kwargs):
        """
        Same constructor as parent class except that if ``cookies_file`` is
        given it'll override the default cookies file.
        """
        for k, v in DEFAULTS.items():
            setattr(self, k, kwargs.pop(k) if k in kwargs else v)
        super(Session, self).__init__(*args, **kwargs)
        self.cookies = LWPCookieJar(self.cookies_file)
        self.load()


    def _set_header_defaults(self, kwargs):
        """
        Internal utility to set default headers on get/post requests.
        """
        headers = {'User-Agent': self.user_agent}
        req_headers = kwargs.pop('headers', {})
        headers.update(req_headers)
        kwargs['headers'] = headers


    def get_url(self, url):
        """
        Get the final URL for a given one. If it starts with a slash (``/``),
        the ``ROOT_URL`` is prepended.
        """
        if url.startswith('/'):
            url = '%s%s' % (ROOT_URL, url)
        return url


    def get(self, url, *args, **kwargs):
        self._set_header_defaults(kwargs)
        url = self.get_url(url)
        return super(Session, self).get(url, *args, **kwargs)


    def post(self, url, *args, **kwargs):
        self._set_header_defaults(kwargs)
        url = self.get_url(url)
        return super(Session, self).post(url, *args, **kwargs)


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
        params = {
            'service': URLS['login_service'],
        }
        url = URLS['login']
        soup = BeautifulSoup(self.get(url, params=params).text)
        lts = soup.select('input[name=lt]')
        if not lts:
            return False
        formkey = lts[0].attrs['value']
        data = {
            'username': username,
            'password': passwd,
            'lt': formkey,
            '_eventId': 'submit',
        }
        resp = self.post(url, params=params, data=data)
        return resp.ok and 'Log In Successful' in resp.text


    def logout(self):
        return self.get_ensure_text(URLS['logout'], 'Logout successful')


    def get_ensure_text(self, url, text, *args, **kw):
        """
        Make a ``GET`` request and test if the given text is present in the
        returned html
        """
        resp = self.get(url, *args, **kw)
        return resp.ok and text in resp.text


    def __del__(self):
        self.save()
