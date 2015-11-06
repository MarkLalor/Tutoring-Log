#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from framework import main
from data.tutee import Tutee  # @UnusedImport for GqlQuery to detect Tutee dataclass.
from data.tutor import Tutor  # @UnusedImport for GqlQuery to detect Tutee dataclass.
from google.appengine.api import users

class Student(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Sorry, only ' + main.restricted_domain() + ' accounts are allowed. <a href = "' + users.create_logout_url("/") + '">Log out</a>')

app = webapp2.WSGIApplication([('/restricted', Student)], debug=main.is_debug())