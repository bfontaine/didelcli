# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

from didel.base import DidelEntity
from didel.souputils import parse_homemade_dl

class CoursePage(DidelEntity):
    """
    A common base for Course-related pages
    """

    def __init__(self, ref):
        super(CoursePage, self).__init__()
        if ref.startswith('/'):
            self.path = ref
        else:
            self.path = self.URL_FMT.format(ref=ref)
        self.ref = ref



class CourseHomework(CoursePage):
    """
    A course homework
    """

    def populate(self, soup, session, **kw):
        content = soup.select('#courseRightContent')[0]
        attrs = parse_homemade_dl(content.select('p small')[0])
        self.title = attrs.get('titre')
        self.begin = attrs.get('du')
        self.end = attrs.get('au')
        self.submission_type = attrs.get('type de soumission')
        self.homework_type = attrs.get('type de travail')
        self.visibility = attrs.get(u'visibilit\xe9 de la soumission')


    def submit(self, student, data):
        """
        Create a new submission for this homework
        """
        pass  # TODO



class CourseHomeworks(CoursePage, list):
    """
    Homeworks list for a course
    """

    URL_FMT = '/claroline/work/work.php?cidReset=true&cidReq={ref}'

    def populate(self, soup, session):
        trs = soup.select('#courseRightContent table tbody tr')
        url = '/claroline/work/%s'
        for tr in trs:
            self.append(CourseHomework(url % tr.select('a')[0].attrs['href']))



class Course(CoursePage):
    """
    A course. It has the following attributes: ``title``, ``teacher``,
    ``about`` and the following sub-resources:
        - ``homeworks``

    Additionally, it keeps a reference to its student with ``student``
    """

    URL_FMT = '/claroline/course/index.php?cid={ref}&cidReset=true&cidReq={ref}'

    def __init__(self, ref, student=None):
        """
        Create a new course from a reference, and an optional student
        """
        super(Course, self).__init__(ref)
        self.student = student
        self.add_resource('homeworks', CourseHomeworks(ref))


    def populate(self, soup, session):
        header = soup.select('.courseInfos')[0]
        self.title = header.select('h2 a')[0].get_text()
        self.teacher = header.select('p')[0].get_text().split('\n')[-1].strip()

        about = soup.select('#portletAbout')
        if about:
            self.about = about[0].get_text().strip()


    def enroll(self):
        """
        Enroll the current student in this course
        """
        path = '/claroline/auth/courses.php'
        text = u'Vous êtes désormais inscrit'
        params = {'cmd': 'exReg', 'course': self.ref}
        return self.session.get_ensure_text(path, text, params=params)


    def unenroll(self):
        """
        Unenroll the current student from this course
        """
        path = '/claroline/auth/courses.php'
        text = u'Vous avez été désinscrit'
        params = {'cmd': 'exUnreg', 'course': self.ref}
        return self.session.get_ensure_text(path, text, params=params)
