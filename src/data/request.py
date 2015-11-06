#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from framework.main import is_debug
from google.appengine.ext import db
import csv
from data.tutor import Tutor
from google.appengine.api import users, memcache
from data.tutoring_session import TutoringSession
import json
from xhtml2pdf import pisa
from six import StringIO


def format_minutes(time):
    hours = time // 60
    minutes = time % 60
    return (str(hours) + (' hours' if hours > 1 else ' hour') if hours > 0 else '') + (' ' + str(minutes) + (' minutes' if minutes > 1 else ' minute') if minutes > 0 else '')


class Request(webapp2.RequestHandler):
    @staticmethod
    def tutorJSONtoPDF(data):
        #If there was nothing retrieved
        if not data:
            return "No data"
        
        rows = ''
        keys = ["tutee_name", "date_tutored", "subject", "minutes"];
        
        entries = len(data['tutor_last'])
        total_minutes = 0
        for i in range(0, entries):
            rows += '<tr>'
            for key in keys:
                
                if key == 'minutes':
                    time = int(data[key][i])
                    rows += '<td class = "normal">' + format_minutes(time) + '</td>'
                    total_minutes += time
                else:
                    rows += '<td class = "normal">' + data[key][i] + '</td>'
            rows += '</tr>'
            
        
        return '''
        <html>
        <head>
        <style type = "text/css">
        @page {
            size: letter portrait;
            @frame content_frame {
                left: 50pt;
                width: 512pt;
                top: 30pt;
                height: 692pt;
            }
        }
        #title
        {
            font-size: 5em;
            font-family: "Times New Roman", Times, serif;
        }
        #info
        {
            font-size: 2em;
        }
        #label, #time
        {
            font-size: 2em;
        }
        div
        {
            text-align: center;
        }
        table
        {
            font-size: 1.4em;
            margin: 30px auto;
        }
        .normal
        {
            border-bottom: 1px solid black;
            padding-top: 3px;
        }
        .head
        {
            font-size: 1.5em;
            padding-bottom: -5px;
            border-bottom: 3px solid black;
        }
        
        </style>
        </head>
        <body>
        <div id = "title" class = "center">Tutoring Log</span></div>
        <div id = "label" class = "center">Mu Alpha Theta - Math Honor Society</div>
        <div id = "label" class = "center">%s %s</div>
        
        <table>
        <thead>
          <tr><td class = "head">Tutee</td><td class = "head">Date</td><td class = "head">Subject</td><td class = "head">Time</td></tr>
        </thead>
        <tbody>
        %s
        </tbody>
        </table>
        <span id = "time">Total: %s</span>
        </body>
        ''' % (data['tutor_first'][0], data['tutor_last'][0], rows, format_minutes(total_minutes))
    
    def get(self):
        ### Database queries ###
        query = self.request.get('query')
        if not query == '' and users.is_current_user_admin():
            if query == 'tutor':
                if self.request.get('type') == 'csv':
                    data = json.loads(self.tutorDataJSON(self.request.get('email')))
                    if not data:
                        self.response.out.write("No data")
                        return
                    
                    self.response.headers['Content-Type'] = 'application/csv'
                    self.response.headers['Content-Disposition'] = str('attachment; filename="' + data['tutor_last'][0] + '_' + data['tutor_first'][0] + '_' + data['tutor_email'][0] + '.csv"')
                    
                    writer = csv.writer(self.response.out)
                    
                    head = ["Tutee Name", "Tutee Email", "Subject", "Date Tutored", "Minutes", "Satisfaction", "Comments", "ID"];
                    keys = ["tutee_name", "tutee_email", "subject", "date_tutored", "minutes", "satisfaction", "comments", "id"];
                    
                    writer.writerow(head)
                    entries = len(data[keys[0]])
                    for i in range(0, entries):
                        row = [];
                        for key in keys:
                            row.append(data[key][i])
                        writer.writerow(row)
                elif self.request.get('type') == 'pdf':
                    data = json.loads(self.tutorDataJSON(self.request.get('email')))
                    self.response.headers['Content-Type'] = 'application/pdf'
                    output = StringIO()
                    pdf = pisa.CreatePDF(Request.tutorJSONtoPDF(data), output, encoding='utf-8')
                    pdf_data = pdf.dest.getvalue()
                    self.response.out.write(pdf_data)
                else:
                    self.response.out.write(self.tutorDataJSON(self.request.get('email')))
                
        ### Item requests ###
        request = self.request.get('r')
        if request == 'tutors':
            self.response.out.write(self.tutorsJSON())
        elif request == 'refreshtutors':
            q = db.GqlQuery("SELECT * FROM Tutor")
            for p in q.run():
                p.delete()
            tutors_file = open("static/tutors.csv", "r")
            reader = csv.reader(tutors_file)
            for line in reader:
                print line
                tutor = Tutor(last=line[0], first=line[1], email=line[2])
                tutor.put()
                
    
    def tutorsJSON(self, should_reload=False):
        #Retrieved cached value
        data = memcache.get('tutors')
        if data is None or should_reload:
            #Load data if not cached
            q = db.GqlQuery("SELECT * FROM Tutor ORDER BY last")
            results = q.run()
            total = []
            for p in results:
                total.append(p.to_dict())
            data = json.dumps(total)
            #Add to cache
            memcache.add('tutors', data, 3600)
        #Return data
        return data
    
    def tutorDataJSON(self, email, should_reload=False):
        key = 'tutor_data_' + email
        data = memcache.get(key)
        if data is None or should_reload:
            q = TutoringSession.all()
            q.filter("tutor_email", email)
            q.order("date_tutored")
            compiled = {}
            for p in q.run(limit=2000):
                session_dict = p.to_dict()
                for key in session_dict.keys():
                    if not key in compiled:
                        compiled[key] = []
                    compiled[key].append(session_dict[key])
            data = json.dumps(compiled)
            memcache.add(key, data, 300) #5 minutes per student
        return data
    
app = webapp2.WSGIApplication([('/request', Request)], debug=is_debug())