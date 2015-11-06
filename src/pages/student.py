#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from framework import main
from framework.config import Configuration
from google.appengine.api import users
from google.appengine.ext import db
from data.tutee import Tutee  # @UnusedImport for GqlQuery to detect Tutee dataclass.
from data.tutor import Tutor  # @UnusedImport for GqlQuery to detect Tutee dataclass.

class Student(webapp2.RequestHandler):
    def get(self):
        if not main.is_valid_user():
            self.redirect('/restricted')
            return

        
        member = main.club_member()
        ### Page Start ###
        main.html_start(self)
        
        ## Head Start ##
        main.head_start(self)
        main.title_set(self, 'Mu Alpha Theta – Tutoring Log – Student')
        
        main.style_print(self, 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css')
        main.style_print(self, 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css')
        main.style_print(self, 'datepicker')
        
        main.head(self) #Common
         
        main.script_print(self, 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js')
        main.script_print(self, 'jquery.numeric.min')
        main.script_print(self, 'jquery.simplemodal.min')
        main.script_print(self, 'datepicker')
        
        main.script_print(self, 'student') #Specific
        
        main.head_end(self)
        ## Head End ##
        
        ## Body Start ##
        main.body_start(self)
        
        ## Header ##
        main.html_print(self, 'header', Configuration.get_instance().title, main.other_pages_html(False, member, users.is_current_user_admin()), main.logout_html());
        
        ## Content ##
        
        #See if name is stored in database
        q = db.GqlQuery("SELECT * FROM Tutee WHERE email = '" + users.get_current_user().email() + "'")
        result = q.get()
        if result == None:
            main.html_print(self, 'student', "")
        else:
            main.html_print(self, 'student', result.name)
        
        main.body_end(self)
        ## Body End ##
        
        main.html_end(self)
        ### Page End ###

app = webapp2.WSGIApplication([('/student', Student)], debug=main.is_debug())