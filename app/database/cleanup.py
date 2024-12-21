from datetime import datetime, timedelta
from app.config import BERLIN_TZ
from app import db

def cleanup_database(database):
    threshold_date = datetime.now(BERLIN_TZ) - timedelta(days=14)

    # Lösche alle alten Einträge in einer einzigen Abfrage
    deleted_count = database.query.filter(database.date_added < threshold_date).delete()
    db.session.commit()

    if deleted_count:
        print(f"{deleted_count} Einträge gelöscht.")
    else:
        print(f"Keine alten Einträge in {database} - Nichts gelöscht")
