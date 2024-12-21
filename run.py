import time
import random
import schedule
from app import create_app
from app.main import random_latest_tweet



app = create_app("development")

with app.app_context():
    # random_latest_tweet()

    # from app.utils.bsky_post import bsky_post_sw
    # bsky_post_sw.tweet("Check das aus Junge: https://fussballwettbonus.com/tipps/1038-lille-sturm-graz-champions-league-tipps-zum-6-spieltag", "https://fussballwettbonus.com/tipps/1038-lille-sturm-graz-champions-league-tipps-zum-6-spieltag")

    # from app.utils.threads_post import post
    # post()

    # from app.utils.helpers import delete_db_entry
    # from app.database.models import BskyDatabase
    # delete_db_entry(3, BskyDatabase)

    schedule.every(random.randint(23,30)).seconds.do(random_latest_tweet)
    while True:
        schedule.run_pending()
        time.sleep(1)




if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False,
        port=4444
    )
