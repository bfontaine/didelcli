# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

try:
    from urlparse import urlparse, parse_qs
except ImportError:  # Python 3
    from urllib.parse import urlparse, parse_qs

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



class CourseAssignment(CoursePage):
    """
    A course assignment
    """

    def __init__(self, path, course_code):
        super(CourseAssignment, self).__init__(path)
        self.course_code = course_code


    def populate(self, soup, session, **kw):
        content = soup.select('#courseRightContent')[0]
        attrs = parse_homemade_dl(content.select('p small')[0])
        self.title = attrs.get('titre')
        self.begin = attrs.get('du')
        self.end = attrs.get('au')
        self.submission_type = attrs.get('type de soumission')
        self.work_type = attrs.get('type de travail')
        self.visibility = attrs.get(u'visibilit\xe9 de la soumission')
        self.assig_id = parse_qs(urlparse(self.path).query)['assigId'][0]


    def submit(self, student, title, datafile, description=''):
        """
        Create a new submission for this assignment
        - ``student``: a ``Student`` object for the currently connected user
        - ``title``: the assignment's title
        - ``datafile``: an open file-like object for the attachment
        - ``description``: an optional description
        """
        authors = '%s %s' % (student.lastname, student.firstname)
        data = {
            'claroFormId': '42',
            'cmd': 'exSubWrk',
            'cidReset': 'true',
            'cidReq': self.course_code,
            'wrkTitle': title,
            'wrkAuthor': authors,
            'wrkTxt': description,
            'submitWrk': 'Ok',
        }
        files = {
            'wrkFile': datafile
        }
        path_fmt = '/claroline/work/user_work.php?assigId={aid}&authId={uid}'
        path = path_fmt.format(aid=self.assig_id, uid=student.auth_id)
        resp = self.session.post(path, data=data, files=files)
        return resp.ok and title in resp.text



class CourseAssignments(CoursePage, list):
    """
    Assignments list for a course
    """

    URL_FMT = '/claroline/work/work.php?cidReset=true&cidReq={ref}'

    def populate(self, soup, session):
        trs = soup.select('#courseRightContent table tbody tr')
        path_fmt = '/claroline/work/%s'
        for tr in trs:
            path = path_fmt % tr.select('a')[0].attrs['href']
            self.append(CourseAssignment(path, self.ref))



class Course(CoursePage):
    """
    A course. It has the following attributes: ``title``, ``teacher``,
    ``about`` and the following sub-resources:
        - ``assignments``

    Additionally, it keeps a reference to its student with ``student``
    """

    URL_FMT = '/claroline/course/index.php?cid={ref}&cidReset=true&cidReq={ref}'

    def __init__(self, ref, student=None):
        """
        Create a new course from a reference, and an optional student
        """
        super(Course, self).__init__(ref)
        self.student = student
        self.add_resource('assignments', CourseAssignments(ref))


    def populate(self, soup, session):
        header = soup.select('.courseInfos')[0]
        self.title = header.select('h2 a')[0].get_text()
        self.teacher = header.select('p')[0].get_text().split('\n')[-1].strip()

        about = soup.select('#portletAbout')
        if about:
            self.about = about[0].get_text().strip()


    def enroll(self, key=None):
        """
        Enroll the current student in this course. Some courses require a key
        to enroll, give it as ``key``.
        """
        path = '/claroline/auth/courses.php'
        ok_text = u'Vous êtes désormais inscrit'
        params = {'cmd': 'exReg', 'course': self.ref}
        if not key:
            return self.session.get_ensure_text(path, ok_text, params=params)
        data = params.copy()
        data['registrationKey'] = 'scade'
        resp = self.session.post(path, params=params, data=data)
        return resp.ok and ok_text in resp.text


    def unenroll(self):
        """
        Unenroll the current student from this course
        """
        path = '/claroline/auth/courses.php'
        text = u'Vous avez été désinscrit'
        params = {'cmd': 'exUnreg', 'course': self.ref}
        return self.session.get_ensure_text(path, text, params=params)
