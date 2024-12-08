import requests
import feedparser
from time import time
from datetime import datetime
from lxml import etree
from app.utils.helpers import already_existing, timedelta_is_ok
from app.database.models import TweetDatabase, BskyDatabase


feeds = [
    "https://fussballwettbonus.com/index.php?option=com_osmap&view=xml&tmpl=component&news=1&id=2",
    "https://fussballwettenbonus.info/alle/news/feed/", "https://fussballwetten24.org/alle/aktuell/feed/",
    "https://gratiswetten.org/bereich/aktuell/feed/", "https://fussballwetten24.org/alle/tipps/feed/",
    "https://gratiswetten.org/bereich/sportwetten-tipps/feed/", "https://fussballwettenbonus.info/alle/tipps/feed/"
    ]

### SITEMAP SCRAPER FÜR FWBCOM
# def process_sitemap(feed_url, database):
    # import xml.etree.ElementTree as ET
#     fwbcom_feed = []
#     response = requests.get(feed_url)
#     response.raise_for_status()  # Fehler bei HTTP-Statuscodes

#     # XML-Daten parsen
#     root = ET.fromstring(response.content)

#     # Namespace definieren
#     namespaces = {'news': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

#     # Alle URLs durchlaufen
#     for url in root.findall('url'):
#         loc = url.find('loc').text
#         news = url.find('news:news', namespaces)

#         if news is not None:
#             title = news.find('news:title', namespaces).text
#             publication_date = news.find('news:publication_date', namespaces).text

#             # Veröffentlichung innerhalb der letzten 48 Stunden?
#             newsdate = datetime.strptime(publication_date, "%Y-%m-%dT%H:%M:%SZ")
#             # newsdate = datetime.strptime(publication_date, "%a, %d %b %Y %H:%M:%S %z")

#             if not already_existing(loc, database) and timedelta_is_ok(newsdate):
#                 print(f"Title: {title}")
#                 print(f"URL: {loc}")
#                 print(f"Published: {publication_date}")
#                 print("---")

#                 fwbcom_feed.append(loc)

#     return fwbcom_feed

# def process_sitemap(feed_url, database):
#     fwbcom_feed = []
#     response = requests.get(feed_url)
#     response.raise_for_status()  # Fehler bei HTTP-Statuscodes

#     # XML-Daten parsen
#     tree = etree.fromstring(response.content)

#     # Namespace definieren
#     namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

#     # Alle URLs durchlaufen
#     for url in tree.xpath('//ns:url', namespaces=namespaces):
#         # Extrahiere 'loc' und 'lastmod'
#         loc = url.xpath('ns:loc/text()', namespaces=namespaces)
#         lastmod = url.xpath('ns:lastmod/text()', namespaces=namespaces)

#         # Debug-Ausgabe: Überprüfe, ob lastmod und loc korrekt extrahiert werden
#         print("Loc:", loc)
#         print("Lastmod:", lastmod)

#         if loc:
#             print(f"URL: {loc[0]}")  # Annahme: 'loc' enthält immer einen Wert
#         if lastmod:
#             print(f"Last modified: {lastmod[0]}")  # Annahme: 'lastmod' enthält immer einen Wert



#         if loc:
#             # Wenn ein `lastmod` vorhanden ist, verwenden wir es, ansonsten setzen wir den aktuellen Zeitpunkt
#             publication_date = lastmod if lastmod else datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

#             # Datum in ein datetime-Objekt umwandeln
#             newsdate = datetime.strptime(publication_date, "%Y-%m-%dT%H:%M:%SZ")

#             print(f"Checking URL: {loc}")  # Debugging-Ausgabe


#             # Veröffentlichung innerhalb der letzten 48 Stunden prüfen
#             if not already_existing(loc, database) and timedelta_is_ok(newsdate):
#                 print(f"URL: {loc}")
#                 print(f"Published: {publication_date}")
#                 print("---")
#                 fwbcom_feed.append(loc)

#     return fwbcom_feed

def process_sitemap(feed_url, database):
    fwbcom_feed = []
    response = requests.get(feed_url)
    response.raise_for_status()  # Fehler bei HTTP-Statuscodes

    # XML-Daten parsen
    tree = etree.fromstring(response.content)

    # Namespaces definieren
    namespaces = {
        'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'news': 'http://www.google.com/schemas/sitemap-news/0.9'
    }

    # Alle URLs durchlaufen
    for url in tree.xpath('//ns:url', namespaces=namespaces):
        # Extrahiere 'loc' und Publikationsdatum
        loc = url.xpath('ns:loc/text()', namespaces=namespaces)
        publication_date = url.xpath('.//news:publication_date/text()', namespaces=namespaces)

        if loc:
            loc = loc[0]

            if publication_date:
                publication_date = publication_date[0]
                # Datum in ein datetime-Objekt umwandeln
                newsdate = datetime.strptime(publication_date, "%Y-%m-%dT%H:%M:%SZ")
            else:
                newsdate = datetime.now()

            # Debugging-Ausgaben
            print(f"URL: {loc}")
            print(f"Published: {publication_date} FORMATIERT: {newsdate}")

            # Veröffentlichung innerhalb der letzten 48 Stunden prüfen
            if not already_existing(loc, database) and timedelta_is_ok(newsdate):
                fwbcom_feed.append(loc)

    return fwbcom_feed



def scrape_rss(url, database):

    fwbcom_feed = []
    feed = []

    if url.startswith("https://fussballwettbonus.com/"):
        print("fwb.com")
        fwbcom_feed = process_sitemap(url, database)


    feedraw = feedparser.parse(url)

    for entry in feedraw.entries:
        newsdate = datetime.strptime(entry.updated, "%a, %d %b %Y %H:%M:%S %z")
        if not already_existing(entry.link, database) and timedelta_is_ok(newsdate):
            # print(type(entry.updated))
            # print(entry.updated_parsed)
            feed.append(entry.link)
    print(fwbcom_feed + feed)
    return fwbcom_feed + feed


if __name__ == "__main__":
    for feed in feeds:
        scrape_rss(feed, TweetDatabase)
        time.sleep(2000)
