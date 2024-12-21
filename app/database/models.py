from datetime import datetime
from app import db
from app.config import BERLIN_TZ



class SocialBase(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=lambda: datetime.now(BERLIN_TZ))  # Standardwert
    url = db.Column(db.String(255))

    def __init__(self, url, date=None):
        self.date = date or datetime.now(BERLIN_TZ)  # Fallback, falls kein Datum übergeben wird
        self.url = url


class TweetDatabase(SocialBase):
    pass

class BskyDatabase(SocialBase):
    pass
