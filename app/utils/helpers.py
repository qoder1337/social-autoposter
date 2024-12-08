# from app.database.models import TweetDatabase, BskyDatabase
from datetime import datetime, timedelta
import pytz

def already_existing(url, database):
    already_existing = database.query.filter_by(url=url).first()
    if already_existing:
        print("URL bereits gepostet. Kein Tweet gesendet.")
        return True
    return False

# def timedelta_is_ok(newsdate):

#     utc_tz = pytz.utc


#     if newsdate.tzinfo is None:

#         try:
#             return newsdate.replace(tzinfo=pytz.timezone(utc_tz))
#         except pytz.UnknownTimeZoneError:
#             raise ValueError(f"Unbekannte Zeitzone")

#     print(newsdate.tzinfo)

#     now = datetime.now(utc_tz)

#     time_diff = now - newsdate
#     if time_diff <= timedelta(hours=48):
#         print("Die News wurde innerhalb der letzten 48 Stunden erstellt.")
#         return True
#     else:
#         print("Die News ist älter als 48 Stunden.")
#         return False
def timedelta_is_ok(newsdate):

    if newsdate.tzinfo is None:
        try:
            newsdate = newsdate.replace(tzinfo=pytz.utc)
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Unbekannte Zeitzone")

    now = datetime.now(pytz.utc)
    time_diff = now - newsdate

    if time_diff <= timedelta(hours=48):
        print("Die News wurde innerhalb der letzten 48 Stunden erstellt.")
        return True
    else:
        print("Die News ist älter als 48 Stunden.")
        return False
