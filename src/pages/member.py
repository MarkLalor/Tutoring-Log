#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from framework.main import is_debug
from google.appengine.api import users
from framework import main
from framework.config import Configuration
from google.appengine.ext import db
from data.tutor import Tutor  # @UnusedImport for GqlQuery to detect Tutee dataclass.
from data.tutoring_session import TutoringSession  # @UnusedImport for GqlQuery to detect TutoringSession dataclass.

class Member(webapp2.RequestHandler):
    def get(self):
        if not main.is_valid_user():
            self.redirect('/restricted')
            return
            
        member = main.club_member()
        
        #Automatically redirect to the student page if they are not a club member
        if not member and not users.is_current_user_admin():
            self.redirect('/student')
            return;
        if not member and users.is_current_user_admin():
            self.redirect('/admin')
            return;
        
        ### Page Start ###
        main.html_start(self)
        
        ## Head Start ##
        main.head_start(self)
        main.title_set(self, 'Mu Alpha Theta – Tutoring Log – Member')
        
        main.style_print(self, 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css')
        main.style_print(self, 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css')
        main.style_print(self, 'member')
        
        main.head(self) #Common
        
        main.script_print(self, 'jquery.simplemodal.min')
        main.script_print(self, 'http://cdnjs.cloudflare.com/ajax/libs/list.js/1.1.1/list.min.js')
        main.script_print(self, 'member') #Specific
        
        main.head_end(self)
        ## Head End ##
        
        ## Body Start ##
        main.body_start(self)
        
        ## Header ##
        main.html_print(self, 'header', Configuration.get_instance().title, main.other_pages_html(True, False, users.is_current_user_admin()), main.logout_html());
        
        ## Content ##
        
        #Retrieve data
        datastring = ''
        qdata = db.GqlQuery("SELECT * FROM TutoringSession WHERE tutor_email = '" + users.get_current_user().email() + "' ORDER BY date_tutored DESC")
        for session in qdata.run(limit=2000):
            datastring += """
            <tr>
                <td class="name">%s</td>
                <td class="email"><a class = "mailto-link" href = "mailto:%s">%s</a></td>
                <td class="date" title = "Logged %s">%s</td>
                <td class="subject">%s</td>
                <td class="minutes">%d</td>
            </tr>
            """ % (session.tutee_name, session.tutee_email, session.tutee_email, session.date_logged.strftime("%Y-%m-%d %H:%M:%S"), session.date_tutored.strftime("%m/%d/%Y"), session.subject, session.minutes)
            
        message = ''
        if not member and not users.is_current_user_admin():
            message = 'Error... could not locate club member data for your email "' + users.get_current_user().email() + '"'
        elif member:
            message = 'Welcome. Displaying log data for <i>' + member.first + ' ' + member.last + '</i> (' + users.get_current_user().email() + ')'
        else:
            message = 'Welcome. You are not a club member but are an administrator, there is nothing to see on this page. See the <a href = "/admin">administrator page</a>. For information.'
        
        main.html_print(self, 'member', message, datastring)
        
        main.body_end(self)
        ## Body End ##
        
        main.html_end(self)
        ### Page End ###

app = webapp2.WSGIApplication([('/member', Member)], debug=is_debug())