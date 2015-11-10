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
    if time == 0:
        return '0'
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
            
        
        with open('static/css/pdf.css', 'r') as f: css = f.read()
        
        return '''
        <html>
        <head>
        <style type = "text/css">%s</style>
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
        </html>
        ''' % (css, data['tutor_first'][0], data['tutor_last'][0], rows, format_minutes(total_minutes))
        
    @staticmethod
    def summaryJSONtoPDF(data):
        #If there was nothing retrieved
        if not data:
            return "No data"
        
        #Open the PDF stylesheet for use with XHTML to PDF.
        with open('static/css/pdf.css', 'r') as f: css = f.read()
        
        rows = ''
        rows2 = ''
        minutes = 0
        
        #Create a row with each tutor's data
        for tutor in data:
            minutes += int(tutor[3])
            
            rows += '<tr>'
            rows += '<td class = "normal">' + str(tutor[0]) + '</td>'
            rows += '<td class = "normal">' + str(tutor[1]) + '</td>'
            rows += '<td class = "normal">' + str(tutor[2]) + '</td>'
            rows += '<td class = "normal">' + format_minutes(tutor[3]) + '</td>'
            rows += '</tr>'
            
        data.sort(key = lambda x: x[3], reverse=True)
        #Create a row with each tutor's data in order of minutes
        for tutor in data:
            rows2 += '<tr>'
            rows2 += '<td class = "normal">' + str(tutor[0]) + '</td>'
            rows2 += '<td class = "normal">' + str(tutor[1]) + '</td>'
            rows2 += '<td class = "normal">' + str(tutor[2]) + '</td>'
            rows2 += '<td class = "normal">' + format_minutes(tutor[3]) + '</td>'
            rows2 += '</tr>'
        
        #Return the created XHTML to be rendered into a PDF.
        return '''
        <html>
        <head>
        <style type = "text/css">%s</style>
        </head>
        <body>
        
        <div id = "title" class = "center">Tutoring Log</span></div>
        <div id = "label" class = "center">Mu Alpha Theta - Math Honor Society</div>
        <div id = "label" class = "center">All Students (Alphabetical)</div>
        
        <table>
        <thead>
          <tr><td class = "head">Name</td><td class = "head">Sessions</td><td class = "head">Tutees</td><td class = "head">Time</td></tr>
        </thead>
        <tbody>
        %s
        </tbody>
        </table>
        
        <table style = "page-break-before: always;">
        <thead>
          <tr><td class = "head">Name</td><td class = "head">Sessions</td><td class = "head">Tutees</td><td class = "head">Time</td></tr>
        </thead>
        <tbody>
        %s
        </tbody>
        </table>
        <span id = "time">Total: %s</span>
        </body>
        </html>
        ''' % (css, rows, rows2, format_minutes(minutes))
    
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
        if 'tutors' in self.request.GET:
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
        elif request == 'summary':
            data = json.loads(self.tutorSummaryJSON())
            self.response.headers['Content-Type'] = 'application/pdf'
            output = StringIO()
            pdf = pisa.CreatePDF(Request.summaryJSONtoPDF(data), output, encoding='utf-8')
            pdf_data = pdf.dest.getvalue()
            self.response.out.write(pdf_data)
                
    
    def tutorsJSON(self, should_reload=False):
        #Retrieved cached value
        data = memcache.get('tutors')
        if data is None or should_reload:
            #Load data if not cached
            q = db.GqlQuery("SELECT * FROM Tutor ORDER BY last")
            #Empty tutors list.
            tutors = []
            #Iterate through all the database results.
            for tutor in q.run(batch_size=200):
                #Add the tutor list data to the tutors list.
                tutors.append(tutor.to_list())
            #Create JSON string to store in memcache.
            data = json.dumps(tutors)
            #Add to cache
            memcache.add('tutors', data, 3600)
        #Return created or cached data
        return data
    
    def tutorSummaryJSON(self, should_reload=False):
        #Retrieved cached summary.
        data = memcache.get('summary')
        #If it does not exist or is expired, create it.
        if data is None or should_reload:
            #Get all the tutors
            tutors = json.loads(self.tutorsJSON())
            summary = []
            # Go through each tutor
            for tutor in tutors:
                first = tutor['first']
                last = tutor['last']
                email = tutor['email']
                #Get their individual data
                data = json.loads(self.tutorDataJSON(email, should_reload))
                
                #Default values to 0.
                minutes, sessions, tutees = (0,)*3
                
                #If there is data for the student, set the minutes, sessions, and tutees.
                if data:
                    minutes_list = [int(n) for n in data['minutes']] #Stored minutes into integer list
                    minutes = sum(minutes_list) #Sum for the total minutes
                    
                    tutees_list = data['tutee_email'] #List all the tutees emails
                    tutees = len(set(tutees_list)) #Find the length of the set of unique email
                    
                    sessions = len(minutes_list) #Number of sessions is equal to the number of entries
                
                #Add row to the summary.
                summary.append([last + ', ' + first, sessions, tutees, minutes])
            #Turn the summary into JSON data.
            data = json.dumps(summary)
            #Cache this value for 5 minutes.
            memcache.add('summary', data, 300)
        return data
    
    def tutorDataJSON(self, email, should_reload=False):
        key = 'tutor_data_' + email
        data = memcache.get(key)
        if data is None or should_reload:
            print "Reloading... " + key
            q = TutoringSession.all()
            q.filter("tutor_email", email)
            q.order("date_tutored")
            compiled = {}
            for p in q.run(limit=2000):
                session_dict = p.to_dict()
                for k in session_dict.keys():
                    if not k in compiled:
                        compiled[k] = []
                    compiled[k].append(session_dict[k])
            data = json.dumps(compiled)
            memcache.add(key=key, value=data, time=300) #5 minutes per student
        return data
    
app = webapp2.WSGIApplication([('/request', Request)], debug=is_debug())