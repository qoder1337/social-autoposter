import time
import random
import schedule
from app import create_app
from app.main import random_latest_tweet, clean_tweet_dbs


app = create_app("development")

with app.app_context():

    schedule.every(random.randint(23,30)).minutes.do(random_latest_tweet)
    schedule.every().monday.do(clean_tweet_dbs)

    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False,
        port=4444
    )
