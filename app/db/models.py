from app import db

class SocialBase(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    url = db.Column(db.String(255))

    def __init__(self, id, date, url):
        self.id = id
        self.date = date
        self.url = url

class PostedOnX(SocialBase):
    pass
