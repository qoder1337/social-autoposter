from datetime import datetime, timedelta
from app.config import BERLIN_TZ
from app.utils.helpers import origin_log_msg
from app import db

def cleanup_database(database):
    threshold_date = datetime.now(BERLIN_TZ) - timedelta(days=14)

    # Lösche alle alten Einträge in einer einzigen Abfrage
    deleted_count = database.query.filter(database.date < threshold_date).delete()
    db.session.commit()

    if deleted_count:
        origin_log_msg(f"{ deleted_count} Einträge gelöscht.")
    else:
        origin_log_msg(f"Keine alten Einträge in {database} - Nichts gelöscht")
