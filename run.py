import time
import random
import schedule
from app import create_app
from app.main import random_latest_tweet, clean_tweet_dbs


app = create_app("production")

# with app.app_context():
#     ### TEST
#     try:
#         random_latest_tweet()
#     except Exception as e:
#         print(e)

#     # schedule.every(random.randint(85, 90)).minutes.do(random_latest_tweet)
#     # schedule.every().monday.do(clean_tweet_dbs)

#     while True:
#         schedule.run_pending()
#         time.sleep(1)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=4444)
