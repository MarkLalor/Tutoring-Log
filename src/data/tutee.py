from google.appengine.ext import db

class Tutee(db.Model):
    email = db.StringProperty()
    name = db.StringProperty()