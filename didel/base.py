# -*- coding: UTF-8 -*-

try:
    from urlparse import urljoin
except ImportError:  # Python 3
    from urllib.parse import urljoin

from bs4 import BeautifulSoup

ROOT_URL = 'http://didel.script.univ-paris-diderot.fr'


class DidelEntity(object):

    def fetch(self, session):
        """
        Fetch ``self.path`` using the given session and call ``self.populate``
        on the returned text
        """
        path = getattr(self, 'path', None)
        if not path:
            return False
        url = urljoin(ROOT_URL, path)
        resp = session.get(url)
        if not resp.ok:
            return False

        soup = BeautifulSoup(resp.text)

        populate = getattr(self, 'populate', None)
        if populate:
            populate(soup)

    def populate(self, soup):
        raise NotImplementedError
