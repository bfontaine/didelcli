# -*- coding: UTF-8 -*-

from didel.base import DidelEntity
from didel.courses import Course
from didel.session import Session
from didel.exceptions import DidelLoginRequired

def login_required(mth):
    """
    An internal decorator to ensure a ``Student`` method is never called with a
    disconnected session.
    """
    def _mth(self, *args, **kw):
        if not self.logged:
            raise DidelLoginRequired()
        return self.mth(*args, **kw)
    _mth.__name__ = mth.__name__
    return _mth


class Student(DidelEntity):
    """
    A virtual student, i.e. a DidEL session
    """

    def __init__(self, username, password, autofetch=True):
        super(Student, self).__init__()
        self.session = Session()
        self.username = username
        self.path = '/claroline/auth/profile.php'
        self._courses = {}  # cache
        self.logged = self.session.login(self.username, password)
        if autofetch:
            self.fetch(self.session)


    @login_required
    def populate(self, soup, *args, **kw):
        aliases = {'officialCode': 'code', 'uidToEdit': 'auth_id'}
        for attr in ('firstname', 'lastname', 'officialCode', 'username',
                'email', 'phone', 'skype', 'uidToEdit'):
            value = soup.select('input#%s' % attr)[0].attrs['value']
            attr = aliases.get(attr, attr)
            setattr(self, attr, value)


    @login_required
    def get_course(self, ref):
        """
        Return a Course object
        """
        if not ref in self._courses:
            c = Course(ref, self)
            c.fetch(self.session)
            self._courses[ref] = c
        return self._courses[ref]
