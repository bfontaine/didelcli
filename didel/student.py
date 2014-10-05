# -*- coding: UTF-8 -*-

from didel.base import DidelEntity
from didel.courses import Course
from didel.session import Session


class Student(DidelEntity):
    """
    A virtual student, i.e. a DidEL sesion
    """

    def __init__(self, username, password):
        self.session = Session()
        self.username = username
        self.session.login(self.username, password)


    def get_course(self, ref):
        c = Course(ref)
        c.fetch(self.session)
        return c
