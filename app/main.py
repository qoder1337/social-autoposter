from app.utils.x_post import x_post_bip
from app.utils.bsky_post import bsky_post_sw
from app.utils.feedreader import feeds, scrape_rss, extract_hashtags
from app.database.models import TweetDatabase, BskyDatabase
import time
import random
import schedule


def random_latest_tweet():

    check_dbs = TweetDatabase, BskyDatabase

    for feed in feeds:

        site_feed = scrape_rss(feed, check_dbs)

        if site_feed:

            # Zufällige Auswahl von Artikeln, abhängig von der Anzahl verfügbarer Artikel
            # min(len(site_feed), 2) -> maximal 2; oder eben 1 wenn len(site_feed) == 1 ist
            articles = random.sample(site_feed, min(len(site_feed), 2))
            ## 2 Artikel -> articles + []; 1 Artikel -> articles + [None]
            article_urls = articles + [None] * (2 - len(articles))  # Ergänze den einen artikel [articles] mit `None`, falls weniger als 2 Artikel

            posting_routine(*article_urls)

        else:
            print(
                f"Keine Artikel im Feed {feed}, um Tweet-Posts zu erstellen."
            )

def posting_routine(article_url_x = None, article_url_bsky = None):
    contentspinner = [
        "Neues #Wetten Update: ",
        "Neuer Artikel: ",
        "Neu: #Sportwetten aktuell - ",
        "Kuck mal hier: ",
        "Jetzt lesen: ",
        "Frisch reingekommen: ",
        "Top-News für #Wettfans: ",
        "Lesenswert: ",
        "Bleib auf dem Laufenden: ",
        "Für dich entdeckt: ",
        "Heißer Tipp: ",
        "Brandneu: ",
        "Tagesaktueller #onlinewetten Tipp: ",
        "Empfohlen für dich: ",
        "Check das aus: ",
    ]

    def create_post(article_url, platform):
        if article_url:
            hashtags = extract_hashtags(article_url)
            tweetcontent = f"{random.choice(contentspinner)}{hashtags} {article_url}"
            platform.tweet(tweetcontent, article_url)
            # print(tweetcontent)
            time.sleep(4)

    create_post(article_url_x, x_post_bip)
    create_post(article_url_bsky, bsky_post_sw)


    # if article_url_x:
    #     hashtags_x = extract_hashtags(article_url_x)
    #     tweetcontent_x = f"{random.choice(contentspinner)}{hashtags_x} {article_url_x}"
    #     x_post_bip.tweet(tweetcontent_x, article_url_x)


    # if article_url_bsky:
    #     hashtags_bsky = extract_hashtags(article_url_bsky)
    #     tweetcontent_bsky = f"{random.choice(contentspinner)}{hashtags_bsky} {article_url_bsky}"
    #     bsky_post_sw.tweet(tweetcontent_bsky, article_url_bsky)
    #             # print(tweetcontent_bsky)

    # time.sleep(1)


def main():
    schedule.every(random.randint(23,30)).seconds.do(random_latest_tweet)
    while True:
        schedule.run_pending()
        time.sleep(1)
