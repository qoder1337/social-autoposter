from app import create_app, db
from app.utils.x_post import x_post_bip
from app.utils.feedreader import *
from app.utils.helpers import *
from app.utils.bsky_post import bsky_post_sw
from app.database.models import TweetDatabase, BskyDatabase



app = create_app("development")

with app.app_context():
    # db.create_all()
    # textinput = "Neuer TWeet-TEST"
    # url = "http://hallo.devonev"


    # # x_post_bip.tweet(textinput, url)

    # textinput2 = "Neuer 123-TEST"

    # bsky_post_sw.tweet(textinput2, url)

    scrape_rss("https://fussballwettbonus.com/index.php?option=com_osmap&view=xml&tmpl=component&news=1&id=2", TweetDatabase)



# if __name__ == "__main__":

    # app.run(
    #     debug=True,
    #     use_reloader=False,
    #     port=4444
    # )
