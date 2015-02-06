# -*- coding: UTF-8 -*-

from didel.base import DidelEntity
from didel.courses import Course
from didel.session import Session
from didel.exceptions import DidelLoginRequired

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

    def populate(self, soup, *args, **kw):
        if not self.logged:
            raise DidelLoginRequired()
        aliases = {'officialCode': 'code', 'uidToEdit': 'auth_id'}
        for attr in ('firstname', 'lastname', 'officialCode', 'username',
                'email', 'phone', 'skype', 'uidToEdit'):
            value = soup.select('input#%s' % attr)[0].attrs['value']
            attr = aliases.get(attr, attr)
            setattr(self, attr, value)


    def get_course(self, ref):
        """
        Return a Course object
        """
        if not self.logged:
            raise DidelLoginRequired()
        if not ref in self._courses:
            c = Course(ref, self)
            c.fetch(self.session)
            self._courses[ref] = c
        return self._courses[ref]


    def get_all_courses(self):
        """
        Return all courses as a list of Course objects
        """
        if not self.logged:
            raise DidelLoginRequired()
        sc = StudentCoursesRefs()
        sc.fetch(self.session)
        # TODO use a generator and/or a subresource?
        return [self.get_course(ref) for ref in sc.refs]



class StudentCoursesRefs(DidelEntity):
    """
    didel main page
    """

    def __init__(self):
        super(StudentCoursesRefs, self).__init__()
        self.path = '/?fromCasServer=true'
        self.refs = []


    def populate(self, soup, *args, **kw):
        """
        save references of courses in a list
        """
        soup_refs = soup.select("dt a")
        self.refs = [cours.attrs["href"].split("=")[1] for cours in soup_refs]
