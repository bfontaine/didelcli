# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

from didel.base import DidelEntity
from didel.souputils import parse_homemade_dl

class CoursePage(DidelEntity):

    def __init__(self, ref):
        super(CoursePage, self).__init__()
        if ref.startswith('/'):
            self.path = ref
        else:
            self.path = self.URL_FMT.format(ref=ref)
        self.ref = ref


class CourseHomework(CoursePage):

    def populate(self, soup, session, **kw):
        content = soup.select('#courseRightContent')[0]
        attrs = parse_homemade_dl(content.select('p small')[0])
        self.title = attrs.get('titre')
        self.begin = attrs.get('du')
        self.end = attrs.get('au')
        self.submission_type = attrs.get('type de soumission')
        self.homework_type = attrs.get('type de travail')
        self.visibility = attrs.get(u'visibilit\xe9 de la soumission')


class CourseHomeworks(CoursePage, list):

    URL_FMT = '/claroline/work/work.php?cidReset=true&cidReq={ref}'

    def populate(self, soup, session):
        trs = soup.select('#courseRightContent table tbody tr')
        url = '/claroline/work/%s'
        for tr in trs:
            self.append(CourseHomework(url % tr.select('a')[0].attrs['href']))


class Course(CoursePage):

    URL_FMT = '/claroline/course/index.php?cid={ref}&cidReset=true&cidReq={ref}'

    def __init__(self, ref):
        super(Course, self).__init__(ref)
        self.add_resource('homeworks', CourseHomeworks(ref))

    def populate(self, soup, session):
        header = soup.select('.courseInfos')[0]
        self.title = header.select('h2 a')[0].get_text()
        self.teacher = header.select('p')[0].get_text().split('\n')[-1].strip()

        about = soup.select('#portletAbout')
        if about:
            self.about = about[0].get_text().strip()
