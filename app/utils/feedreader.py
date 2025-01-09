import requests
import feedparser
from datetime import datetime
from lxml import etree
from app.utils.helpers import already_existing, timedelta_is_ok


def process_sitemap(feed_url, databases):
    feed = []
    response = requests.get(feed_url)
    # print(response.text)
    response.raise_for_status()  # Fehler bei HTTP-Statuscodes

    # XML-Daten parsen
    # tree = etree.fromstring(response.content)

    parser = etree.XMLParser()
    tree = etree.fromstring(response.content, parser)

    # Namespaces definieren
    namespaces = {
        "ns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "news": "http://www.google.com/schemas/sitemap-news/0.9",
    }

    # Alle URLs durchlaufen
    for url in tree.xpath("//ns:url", namespaces=namespaces):
        # Extrahiere 'loc' und Publikationsdatum
        loc = url.xpath("ns:loc/text()", namespaces=namespaces)
        publication_date = url.xpath(
            ".//news:publication_date/text()", namespaces=namespaces
        )

        if loc:
            loc = loc[0]

            if publication_date:
                publication_date = publication_date[0]
                # Datum in ein datetime-Objekt umwandeln
                newsdate = datetime.strptime(publication_date, "%Y-%m-%dT%H:%M:%SZ")
            else:
                newsdate = datetime.now()

            # Debugging-Ausgaben
            # print(f"URL: {loc}")
            # print(f"Published: {publication_date} FORMATIERT: {newsdate}")

            # Veröffentlichung innerhalb der letzten 48 Stunden prüfen
            if not already_existing(loc, databases) and timedelta_is_ok(newsdate):
                feed.append(loc)

    return feed


def scrape_rss(url, databases):
    sitemap_feed = []
    feed = []

    # Filter für XML Dateien
    if "xml" in url:
        print(f"Weiterleitung an xml Scraper für: {url}")
        sitemap_feed = process_sitemap(url, databases)

    feedraw = feedparser.parse(url)

    for entry in feedraw.entries:
        newsdate = datetime.strptime(entry.updated, "%a, %d %b %Y %H:%M:%S %z")
        if not already_existing(entry.link, databases) and timedelta_is_ok(newsdate):
            # print(type(entry.updated))
            # print(entry.updated_parsed)
            feed.append(entry.link)
    return sitemap_feed + feed


def extract_hashtags(input_url):
    ### ggf noch erweitern
    remove_words = "spieltag"

    url_splits = input_url.split("/")
    url_slug = [x.strip() for x in url_splits if x][-1].split("-")
    filtered_slug = filter(
        lambda x: len(x) > 3 and x.isalpha() and x not in remove_words, url_slug
    )

    return " ".join(f"#{word}" for word in filtered_slug)
