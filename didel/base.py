# -*- coding: UTF-8 -*-

try:
    from urlparse import urljoin
except ImportError:  # Python 3
    from urllib.parse import urljoin

from bs4 import BeautifulSoup

ROOT_URL = 'http://didel.script.univ-paris-diderot.fr'


class DidelEntity(object):

    def __init__(self, *args, **kwargs):
        self._resources = {}

    def fetch(self, session):
        """
        Fetch ``self.path`` using the given session and call ``self.populate``
        on the returned text
        """
        populate = getattr(self, 'populate', None)
        if not populate or self.is_populated():
            return False

        path = getattr(self, 'path', None)
        if not path:
            return False
        url = urljoin(ROOT_URL, path)
        resp = session.get(url)
        if not resp.ok:
            return False

        soup = BeautifulSoup(resp.text, 'lxml')

        setattr(self, 'session', session)
        populate(soup, session)
        setattr(self, '_populated', True)

    def populate(self, soup, session, **kwargs):
        raise NotImplementedError

    def is_populated(self):
        """
        Test if the element has been populated
        """
        return getattr(self, '_populated', False)

    def add_resource(self, name, value):
        """
        Add a subresource to this element
        """
        self._resources[name] = value

    def __getattr__(self, name):
        """
        Lazily populate subresources when they're acceded
        """
        if name not in self._resources:
            return super(DidelEntity, self).__getattr__(name)

        if not self.is_populated():
            raise Exception('%s is not populated' % repr(self))

        res = self._resources[name]
        res.fetch(self.session)
        setattr(self, name, res)
        return res

    def __getitem__(self, idx):
        """
        Lazily populate subresources when they're acceded
        """
        el = super(DidelEntity, self).__getitem__(idx)
        el.fetch(self.session)
        return el
