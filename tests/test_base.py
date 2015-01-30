# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

try:
    from urlparse import urljoin
except ImportError:  # Python 3
    from urllib.parse import urljoin

from bs4 import BeautifulSoup
import responses

from didel.base import DidelEntity, DidelError, ROOT_URL
from didel.session import Session


class PopulatedDidelEntity(DidelEntity):
    def populate(self, *args, **kw):
        pass


class ListPopulatedDidelEntity(PopulatedDidelEntity, list):
    pass


class TestBase(unittest.TestCase):

    def url(self, path):
        return urljoin(ROOT_URL, path)

    def setUp(self):
        self.session = Session()
        self.soup = BeautifulSoup('')
        self._DidelEntity_populate = DidelEntity.populate

    def tearDown(self):
        DidelEntity.populate = self._DidelEntity_populate

    def test_base_entity_should_not_be_populated(self):
        e = DidelEntity()
        self.assertFalse(e.is_populated())

    def test_base_url(self):
        path = 'xzrd1d$z9'
        e = DidelEntity()
        e.path = path
        self.assertEquals(self.url(path), e.url())

    def test_trying_to_access_subresource_fails_if_not_populated(self):
        e = DidelEntity()
        e.add_resource('foo', DidelEntity())
        self.assertRaises(DidelError, lambda: e.foo)

    def test_dont_fetch_without_populate_method(self):
        e = DidelEntity()
        delattr(DidelEntity, 'populate')
        self.assertFalse(e.fetch(self.session))

    def test_dont_fetch_without_path(self):
        e = DidelEntity()
        self.assertFalse(e.fetch(self.session))

    def test_populate_not_implemented_on_base_class(self):
        e = DidelEntity()
        self.assertRaises(NotImplementedError,
                lambda: e.populate(self.soup, self.session))

    @responses.activate
    def test_404_fetch_error(self):
        path = '/foobar/xzurgsa/1/23/42-3.14'
        body = 'xozers12deA=41.'
        e = DidelEntity()
        e.path = path
        responses.add(responses.GET, self.url(path),
                body=body, status=404)
        self.assertFalse(e.fetch(self.session))
        self.assertEquals(1, len(responses.calls))
        self.assertEquals(body, responses.calls[0].response.text)

    @responses.activate
    def test_500_fetch_error(self):
        path = '/foobar/xzurgsa/1/23/42-3.14'
        body = 'xozers12deA=41.'
        e = DidelEntity()
        e.path = path
        responses.add(responses.GET, self.url(path), body=body, status=500)
        self.assertFalse(e.fetch(self.session))
        self.assertEquals(1, len(responses.calls))
        self.assertEquals(body, responses.calls[0].response.text)

    @responses.activate
    def test_fetch_calls_populate(self):
        populate_args = []
        text = 'foo'
        path = '/foo/b/ar/x123=ae2-a'

        class A(DidelEntity):
            def populate(self, *args, **kw):
                populate_args.extend(args)

        e = A()
        e.path = path
        responses.add(responses.GET, self.url(path), body=text, status=200)
        self.assertTrue(e.fetch(self.session))
        self.assertEquals(self.session, e.session)
        self.assertEquals(2, len(populate_args))
        self.assertEquals(self.session, populate_args[1])
        self.assertEquals(text, populate_args[0].get_text())

    @responses.activate
    def test_fetched_is_populated(self):
        path = '/foo/b/ar/x123=ae2-bc'
        e = PopulatedDidelEntity()
        e.path = path
        responses.add(responses.GET, self.url(path), body='x', status=200)
        self.assertFalse(e.is_populated())
        self.assertTrue(e.fetch(self.session))
        self.assertTrue(e.is_populated())

    @responses.activate
    def test_subresource_access_fetches_it(self):
        parentpath, childpath = '/xyz/123/abcq', '/qux/e-123'
        childname = 'xyzAxq'
        parent = PopulatedDidelEntity()
        child = PopulatedDidelEntity()
        parent.path, child.path = parentpath, childpath
        parent.add_resource(childname, child)
        responses.add(responses.GET, self.url(parentpath), body='x', status=200)
        responses.add(responses.GET, self.url(childpath), body='x', status=200)
        self.assertTrue(parent.fetch(self.session))
        self.assertFalse(child.is_populated())
        self.assertEquals(child, getattr(parent, childname))
        self.assertTrue(child.is_populated())

    @responses.activate
    def test_list_subresource_access_fetches_it(self):
        parentpath, childpath = '/xyz/123/abcq', '/qux/e-123'
        parent = ListPopulatedDidelEntity()
        child = PopulatedDidelEntity()
        parent.path, child.path = parentpath, childpath
        parent.append(child)
        responses.add(responses.GET, self.url(parentpath), body='x', status=200)
        responses.add(responses.GET, self.url(childpath), body='x', status=200)
        self.assertTrue(parent.fetch(self.session))
        self.assertFalse(child.is_populated())
        self.assertEquals(child, parent[0])
        self.assertTrue(child.is_populated())
