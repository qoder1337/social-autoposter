import time
import random
from app.database.cleanup import cleanup_database
from app.database.models import TweetDatabase, BskyDatabase
from app.utils import (
    x_post_bip,
    bsky_post_sw,
    feeds,
    contentspinner,
    scrape_rss,
    extract_hashtags,
)

check_dbs = TweetDatabase, BskyDatabase


def clean_tweet_dbs():
    for database in check_dbs:
        cleanup_database(database)


def random_latest_tweet():
    # feeds beinhaltet eine simple Liste aus Feed-URLS (zb WP-Feed, oder auch xml sitemap Feed)
    for feed in feeds:
        site_feed = scrape_rss(feed, check_dbs)

        if site_feed:
            # Zufällige Auswahl von Artikeln, abhängig von der Anzahl verfügbarer Artikel
            # min(len(site_feed), 2) -> maximal 2; oder eben 1 wenn len(site_feed) == 1 ist
            articles = random.sample(site_feed, min(len(site_feed), 2))
            ## 2 Artikel -> [articles] + []; 1 Artikel -> [articles] + [None]
            article_urls = articles + [None] * (2 - len(articles))
            posting_routine(*article_urls)

        else:
            print(f"Keine Artikel im Feed {feed}, um Tweet-Posts zu erstellen.")


def posting_routine(article_url_x=None, article_url_bsky=None):
    def create_post(article_url, platform):
        if article_url:
            hashtags = extract_hashtags(article_url)
            tweetcontent = f"{random.choice(contentspinner)}{hashtags} {article_url}"
            platform.tweet(tweetcontent, article_url)
            # print(tweetcontent)
            time.sleep(4)

    create_post(article_url_x, x_post_bip)
    create_post(article_url_bsky, bsky_post_sw)
