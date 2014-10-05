# -*- coding: UTF-8 -*-

from didel.base import DidelEntity

class Course(DidelEntity):

    URL_FMT = '/claroline/course/index.php?cid={ref}&cidReset=true&cidReq={ref}'

    def __init__(self, ref):
        if ref.startswith('/'):
            self.path = ref
        else:
            self.path = self.URL_FMT.format(ref=ref)
        self.ref = ref

    def populate(self, soup):
        header = soup.select('.courseInfos')[0]
        self.title = header.select('h2 a')[0].get_text()
        self.teacher = header.select('p')[0].get_text().split('\n')[-1].strip()

        about = soup.select('#portletAbout')
        if about:
            self.about = about[0].get_text().strip()

        # TODO
