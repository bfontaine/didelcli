# -*- coding: UTF-8 -*-

try:
    from urlparse import urljoin
except ImportError:  # Python 3
    from urllib.parse import urljoin

from bs4 import BeautifulSoup

ROOT_URL = 'http://didel.script.univ-paris-diderot.fr'

class DidelError(Exception):
    """
    Base exception for Didel errors
    """

    pass


class DidelEntity(object):
    """
    Common base for all fetchable entities. It provides a convenient way to
    fetch a page describing an entity and populate the object with it.

    Usage: ::

        class MyEntity(DidelEntity):

            def __init__(self, someArg):
                self.path = '/foo/bar/qux/%s.html' % someArg
                super(MyEntity, self).__init__()

            def populate(self, soup, session, **kw):
                # populate the object with ``soup``
                self.title = soup.select('h1')[0].get_text()

    The entity can then be populated: ::

        s = Session()
        m = MyEntity("foo")
        m.fetch(s)
        print m.title
    """

    def __init__(self, *args, **kwargs):
        self._resources = {}


    def url(self):
        """
        Return this entity's URL
        """
        return urljoin(ROOT_URL, self.path)


    def fetch(self, session):
        """
        Fetch ``self.path`` using the given session and call ``self.populate``
        on the returned text.
        It sets ``self.session`` to the given session and ``self._populated``
        to ``True``.
        """
        if not hasattr(self, 'populate') or self.is_populated():
            return False

        if not hasattr(self, 'path'):
            return False
        url = self.url()
        resp = session.get(url)
        if not resp.ok:
            return False

        soup = BeautifulSoup(resp.text, 'lxml')

        setattr(self, 'session', session)
        self.populate(soup, session)
        setattr(self, '_populated', True)
        return True


    def populate(self, soup, session, **kwargs):
        """
        This should be implemented by subclasses
        """
        raise NotImplementedError


    def is_populated(self):
        """
        Test if the element has been populated
        """
        return hasattr(self, '_populated')


    def add_resource(self, name, value):
        """
        Add a subresource to this element. It should be a ``DidelEntity``.
        ``name`` will be used as an attribute name which will, when first
        acceded, populate the subresource and cache it.
        """
        self._resources[name] = value


    def __getattr__(self, name):
        """
        Lazily populate subresources when they're acceded
        """
        if name not in self._resources:
            raise AttributeError("'%s' has no attribute '%s'" % (self, name))

        if not self.is_populated():
            raise DidelError('%s is not populated' % repr(self))

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
