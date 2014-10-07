# -*- coding: UTF-8 -*-

from didel.base import DidelEntity
from didel.courses import Course
from didel.session import Session


class Student(DidelEntity):
    """
    A virtual student, i.e. a DidEL sesion
    """

    def __init__(self, username, password):
        super(Student, self).__init__()
        self.session = Session()
        self.username = username
        self.session.login(self.username, password)
        self.path = '/claroline/auth/profile.php'
        self._courses = {}


    def populate(self, soup, *args, **kw):
        aliases = {'officialCode': 'code', 'uiToEdit': 'auth_id'}
        for attr in ('firstname', 'lastname', 'officialCode', 'username',
                'email', 'phone', 'skype', 'uiToEdit'):
            value = soup.select('input#%s' % attr)[0].attrs['value']
            attr = aliases.get(attr, attr)
            setattr(self, attr, value)


    def get_course(self, ref):
        """
        Return a Course object
        """
        if not ref in self._courses:
            c = Course(ref, self)
            c.fetch(self.session)
            self._courses[ref] = c
        return self._courses[ref]
