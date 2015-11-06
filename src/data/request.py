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

class Request(webapp2.RequestHandler):
    def get(self):
        ### Database queries ###
        query = self.request.get('query')
        if not query == '' and users.is_current_user_admin():
            if query == 'tutor':
                if self.request.get('data2') == 'csv':
                    data = json.loads(self.tutorDataJSON(self.request.get('data1')))
                    
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
                else:
                    self.response.out.write(self.tutorDataJSON(self.request.get('data1')))
                
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