from datetime import datetime
from pytz import timezone
from app import db

# Berlin-Zeitzone definieren
berlin_tz = timezone("Europe/Berlin")

class SocialBase(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=lambda: datetime.now(berlin_tz))  # Standardwert
    url = db.Column(db.String(255))

    def __init__(self, url, date=None):
        self.date = date or datetime.now(berlin_tz)  # Fallback, falls kein Datum übergeben wird
        self.url = url


class TweetDatabase(SocialBase):
    pass

class BskyDatabase(SocialBase):
    pass
