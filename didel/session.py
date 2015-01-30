# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from requests import Session as BaseSession

from didel.base import ROOT_URL
from didel.exceptions import DidelServerError


URLS = {
    'login': 'https://auth.univ-paris-diderot.fr/cas/login',

    'login_service':
        'http://didel.script.univ-paris-diderot.fr/claroline/auth/login.php' \
        '?authModeReq=CAS',
}

HEADERS = {
    'User-Agent': 'Python/DidelCli +b@ptistefontaine.fr',
}


class Session(BaseSession):
    """
    A session with built-in authentification support for Paris Diderot's
    websites.
    """

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.headers.update(HEADERS)


    def get_url(self, url):
        """
        Get the final URL for a given one. If it starts with a slash (``/``),
        the ``ROOT_URL`` is prepended.
        """
        if url.startswith('/'):
            url = '%s%s' % (ROOT_URL, url)
        return url


    def get(self, url, *args, **kwargs):
        url = self.get_url(url)
        return super(Session, self).get(url, *args, **kwargs)


    def post(self, url, *args, **kwargs):
        url = self.get_url(url)
        return super(Session, self).post(url, *args, **kwargs)


    def check_response(self, resp):
        """
        Check a response and returns ``True`` if it has a success status code,
        or raises a ``DidelServerError`` if not.
        """
        if resp.ok:
            return True
        raise DidelServerError(resp)


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
        return self.check_response(resp) and 'Quitter' in resp.text


    def get_ensure_text(self, url, text, *args, **kw):
        """
        Make a ``GET`` request and test if the given text is present in the
        returned html
        """
        resp = self.get(url, *args, **kw)
        return self.check_response(resp) and text in resp.text
