# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

try:
    from urlparse import urlparse, parse_qs
except ImportError:  # Python 3
    from urllib.parse import urlparse, parse_qs

from didel.base import DidelEntity
from didel.fileutils import date2timestamp, mkdir_p, file_mtime
from didel.souputils import parse_homemade_dl
import re, os

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


    def synchronize_docs(self, path):
        """
        Synchronize the documents in the given path with the ones from the
        courses followed by the student. The path will be created and populated
        if it doesn't exist.
        """
        d = DocumentsLinks(self.ref)
        d.fetch(self.session)
        d.synchronize(path)


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
        Unenroll the current student from this course.
        """
        path = '/claroline/auth/courses.php'
        text = u'Vous avez été désinscrit'
        params = {'cmd': 'exUnreg', 'course': self.ref}
        return self.session.get_ensure_text(path, text, params=params)


class DocumentsLinks(DidelEntity):

    URL_FMT = '/claroline/document/document.php?cidReset=true&cidReq={ref}'

    def __init__(self, ref, path=None):
        super(DocumentsLinks, self).__init__()
        self.ressources = {}
        self.ref = ref
        if path :
            self.path = path
            self.ref = ""
        else:
            self.path = self.URL_FMT.format(ref=ref)


    def populate(self, soup, session):
        """
        Get all documents and folder from a course.
        """
        table = soup.select(".claroTable tbody tr[align=center]")
        for line in table:
            cols = line.select("td")
            item = cols[0].select(".item")[0]
            name = item.contents[1].strip()
            date = cols[2].select("small")[0].contents[0].strip()
            url = cols[0].select("a")[0].attrs["href"].strip()
            # TODO use a selector here
            if re.match(r"^<img (alt=\"\")? src=\"/web/img/folder", str(item.select("img")[0])):
                doc = DocumentsLinks("", url)
                doc.fetch(self.session)
            else:
                doc = Document(name, url, date)
            self.add_resource(name, doc)


    def synchronize(self, path):
        """
        compare files on didel with file in folder,
            and calling download add or reset files'user
            only if not exist or older
        """
        path = "%s/%s" % (path, self.ref)
        mkdir_p(path)
        for k, resource in self._resources.items():
            if isinstance(resource, DocumentsLinks):
                resource.synchronize("%s/%s" % (path, k))
            else:
                no_file = not os.path.exists("%s/%s" % (path, k))
                didel_time = date2timestamp(resource.date)
                if no_file or didel_time > file_mtime("%s/%s" % (path, k)):
                    self.download(resource, path)


    # TODO move this on the Document class
    def download(self, document, path):
        """
        Download a document in a given path, provided that the parent
        directories already exist
        """
        response = self.session.get(document.url)
        document.path = "%s/%s" % (path, document.name)
        with open(document.path, 'w') as file:
            # TODO use a binary stream here
            file.write(response.content)



class Document(object):

    def __init__(self, name, url, date):
        self.name = name
        self.url = url
        self.date = date

