#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from framework.main import is_debug
from framework import main
from framework.config import Configuration
from google.appengine.api import users

class Admin(webapp2.RequestHandler):
    def get(self):
        if not main.is_valid_user():
            self.redirect('/restricted')
            return
        
        if not users.is_current_user_admin():
            self.redirect('/student')
            return
        
        ### Page Start ###
        main.html_start(self)
        
        ## Head Start ##
        main.head_start(self)
        main.title_set(self, 'Mu Alpha Theta – Tutoring Log – Administrator')
        
        main.style_print(self, 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css')
        main.style_print(self, 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css')
        main.style_print(self, 'admin')
        
        main.head(self) #Common
        
        main.script_print(self, 'jquery.simplemodal.min')
        main.script_print(self, 'http://cdnjs.cloudflare.com/ajax/libs/list.js/1.1.1/list.min.js')
        main.script_print(self, 'admin') #Specific
        
        main.head_end(self)
        ## Head End ##
        
        ## Body Start ##
        main.body_start(self)
        
        ## Header ##
        main.html_print(self, 'header', Configuration.get_instance().title, main.other_pages_html(True, True, False), main.logout_html());
        
        ## Content ##
        
        main.html_print(self, 'admin')
        
        main.body_end(self)
        ## Body End ##
        
        main.html_end(self)
        ### Page End ###

app = webapp2.WSGIApplication([('/admin', Admin)], debug=is_debug())