# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from os import remove
from tempfile import NamedTemporaryFile

import requests
import responses

from didel.session import Session, URLS, ROOT_URL

class FakeSession(Session):
    def __init__(self, *args, **kw):
        kw.setdefault('cookies_file', None)
        super(FakeSession, self).__init__(*args, **kw)


class StoragelessSession(FakeSession):
    def load(self, *args, **kw):
        setattr(self, '_test_load_called', True)
        return True

    def save(self, *args, **kw):
        setattr(self, '_test_save_called', True)
        return True


class TestSession(unittest.TestCase):

    def test_session_is_loaded_on_init(self):
        s = StoragelessSession()
        self.assertTrue(getattr(s, '_test_load_called', False))

    def test_cookies_file_set_on_init(self):
        cf = 'foobarx1/aap./q/dont/exist'
        s = FakeSession(cookies_file=cf)
        self.assertEquals(cf, s.cookies_file)

    def test_ua_set_on_init(self):
        ua = 'th+is/an user 4gent'
        s = FakeSession(user_agent=ua)
        self.assertEquals(ua, s.user_agent)

    def test_set_headers_defaults_user_agent_already_present(self):
        ua = 'some/random - user+agent v42.1.3.21'
        kwargs = {'headers': {'User-Agent': ua}}
        s = FakeSession(user_agent='another/user_agent v1')
        s._set_header_defaults(kwargs)  # in-place change
        self.assertEquals(ua, kwargs['headers']['User-Agent'])

    def test_set_headers_defaults_user_agent_not_present_no_headers(self):
        ua = 'some/random - user+agent v42.1.3.21'
        kwargs = {}
        s = FakeSession(user_agent=ua)
        s._set_header_defaults(kwargs)  # in-place change
        self.assertIn('headers', kwargs)
        self.assertEquals(ua, kwargs['headers']['User-Agent'])

    def test_set_headers_defaults_user_agent_not_present_with_headers(self):
        ua = 'some/random - user+agent v42.1.3.21'
        kwargs = {'headers': {'X-Foo': '42'}}
        s = FakeSession(user_agent=ua)
        s._set_header_defaults(kwargs)  # in-place change
        self.assertIn('headers', kwargs)
        self.assertEquals(ua, kwargs['headers']['User-Agent'])


    # .get_url

    def test_get_absolute_url(self):
        url = 'http://example.com'
        s = FakeSession()
        self.assertEquals(url, s.get_url(url))

    def test_get_relative_url_root(self):
        url = '/'
        s = FakeSession()
        self.assertEquals('%s/' % ROOT_URL, s.get_url(url))

    def test_get_relative_url(self):
        url = '/foo/bar/qux'
        s = FakeSession()
        self.assertEquals('%s%s' % (ROOT_URL, url), s.get_url(url))


    # .get

    @responses.activate
    def test_get_requests_object(self):
        url = 'http://www.example.com/foo'
        body = "okx&Asq'"
        responses.add(responses.GET, url, body=body, status=200)
        s = FakeSession()
        resp = s.get(url)
        self.assertEquals(1, len(responses.calls))
        self.assertIsInstance(resp, requests.Response)

    @responses.activate
    def test_get_set_default_ua(self):
        url = 'http://www.example.com/foo'
        responses.add(responses.GET, url, body='ok', status=200)
        FakeSession().get(url)
        self.assertEquals(1, len(responses.calls))
        self.assertIn('User-Agent', responses.calls[0].request.headers)

    @responses.activate
    def test_post_requests_object(self):
        url = 'http://www.example.com/foo'
        body = "okx&Asq'"
        responses.add(responses.POST, url, body=body, status=200)
        s = FakeSession()
        resp = s.post(url)
        self.assertEquals(1, len(responses.calls))
        self.assertIsInstance(resp, requests.Response)


    # .save

    def test_save_false_on_error(self):
        s = FakeSession(cookies_file='/th/is/pa/t/h/does/n/t/exist')
        self.assertFalse(s.save())

    def test_save_true_on_success(self):
        f = NamedTemporaryFile(delete=False)
        f.close()
        s = FakeSession(cookies_file=f.name)
        self.assertTrue(s.save())
        remove(f.name)

    def test_load_false_on_error(self):
        s = FakeSession(cookies_file='/th/is/pa/t/h/does/n/t/exist')
        self.assertFalse(s.load())

    def test_load_true_on_success(self):
        f = NamedTemporaryFile(delete=False)
        f.close()
        s = FakeSession(cookies_file=f.name)
        self.assertTrue(s.save())
        self.assertTrue(s.load())
        remove(f.name)

    # TODO: login

    @responses.activate
    def test_logout_false_on_error(self):
        url = URLS['logout']
        responses.add(responses.GET, url, body='nope', status=500)
        s = FakeSession()
        self.assertFalse(s.logout())
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_logout_false_without_match(self):
        url = URLS['logout']
        responses.add(responses.GET, url, body='nothing here', status=200)
        s = FakeSession()
        self.assertFalse(s.logout())
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_logout_true_on_success(self):
        url = URLS['logout']
        responses.add(responses.GET, url, body="""
            Logout successful :) """, status=200)
        s = FakeSession()
        self.assertTrue(s.logout())
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_get_ensure_text_false_on_error(self):
        path = '/foo/xyz/aq1'
        url = '%s%s' % (ROOT_URL, path)
        responses.add(responses.GET, url, body='oops', status=404)
        s = FakeSession()
        self.assertFalse(s.get_ensure_text(path, 'oops'))
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_get_ensure_text_false_without_match(self):
        path = '/foo/xyz/aq1'
        url = '%s%s' % (ROOT_URL, path)
        responses.add(responses.GET, url, body="that's ok", status=200)
        s = FakeSession()
        self.assertFalse(s.get_ensure_text(path, 'not ok'))
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_get_ensure_text_false_without_case_sensitive_match(self):
        path = '/foo/xyz/aq1'
        url = '%s%s' % (ROOT_URL, path)
        responses.add(responses.GET, url, body="that's ok", status=200)
        s = FakeSession()
        self.assertFalse(s.get_ensure_text(path, 'OK'))
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_get_ensure_text_true_on_match(self):
        path = '/foo/xyz/aq1'
        url = '%s%s' % (ROOT_URL, path)
        ok = 'okaayy'
        responses.add(responses.GET, url, body="(a%sx" % ok, status=200)
        s = FakeSession()
        self.assertTrue(s.get_ensure_text(path, ok))
        self.assertEquals(1, len(responses.calls))
