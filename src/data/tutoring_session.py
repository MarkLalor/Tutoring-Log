from google.appengine.ext import db

class TutoringSession(db.Model):
    tutor_email = db.StringProperty()
    tutor_last = db.StringProperty()
    tutor_first = db.StringProperty()
    
    tutee_email = db.StringProperty()
    tutee_name = db.StringProperty()
    
    date_logged = db.DateTimeProperty()
    date_tutored = db.DateProperty()
    
    minutes = db.IntegerProperty()
    subject = db.StringProperty()
    comments = db.StringProperty()
    satisfaction = db.IntegerProperty()
    
    def to_dict(self):
        return merge_dicts(dict([(p, unicode(getattr(self, p))) for p in self.properties()]), dict([('id', self.key().id())]))
    
    
def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z