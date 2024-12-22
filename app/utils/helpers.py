from datetime import datetime, timedelta
import pytz
from app import db
import inspect

def origin_log_msg(message):
    current_function = inspect.currentframe().f_back.f_code.co_name
    print(f"[[{current_function}]] {message}")

def delete_db_entry(id, db_name):
    get_by_id = db_name.query.filter_by(id=id).first()

    if get_by_id:
        db.session.delete(get_by_id)
        db.session.commit()
        print(f"Artikel mit id {id} gelöscht!!!!")

def already_existing(url, databases):
    for database in databases:
        already_existing = database.query.filter_by(url=url).first()
        if already_existing:
            print("Vorab Check - URL bereits gepostet. Kein Tweet gesendet.")
            return True
    return False


def timedelta_is_ok(newsdate):

    if newsdate.tzinfo is None:
        try:
            newsdate = newsdate.replace(tzinfo=pytz.utc)
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Unbekannte Zeitzone")

    now = datetime.now(pytz.utc)
    time_diff = now - newsdate

    if time_diff <= timedelta(hours=48):
        # print("Die News wurde innerhalb der letzten 48 Stunden erstellt.")
        return True
    else:
        # print("Die News ist älter als 48 Stunden.")
        return False
