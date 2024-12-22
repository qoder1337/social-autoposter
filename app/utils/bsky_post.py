import os
import re
import json
import requests
import traceback
from app import db
from app.utils import _log_message_
from datetime import datetime, timezone
from app.utils.helpers import origin_log_msg
from app.database.models import BskyDatabase
from dotenv import load_dotenv

load_dotenv()

bsky_dict = {
    "sportwetten": {
        "consumer_key" : os.getenv("BLUESKYSPORTWETTEN_HANDLE"),
        "consumer_secret" : os.getenv("BLUESKYSPORTWETTEN_APP_PASSWORD"),
    }
}

class BaseforBsky():
    def __init__(self, bskyuser):
        if bskyuser not in bsky_dict:
            raise ValueError(f"Unknown bskyuser: {bskyuser}")

        self.consumer_key = bsky_dict[bskyuser]["consumer_key"]
        self.consumer_secret = bsky_dict[bskyuser]["consumer_secret"]
        self.session = None

    def create_session(self):

        try:
            _log_message_.message_handle(
                msg=f"bsky create_session Payload: \
                    {{'identifier': {self.consumer_key}, \
                    'password': {'*' * len(self.consumer_secret)}}}",
                level="info",
            )

            ### SESSION ANFRAGE
            resp = requests.post(
                "https://bsky.social/xrpc/com.atproto.server.createSession",
                json={"identifier": self.consumer_key, "password": self.consumer_secret},
            )
            _log_message_.message_handle(
                    msg=f"Response Status: {resp.status_code}",
                    level="info",
                )
            _log_message_.message_handle(
                    msg=f"Response Text: {resp.text}",
                    level="info",
                )

            resp.raise_for_status()
            self.session = resp.json()
            print(self.session["accessJwt"])

        except Exception as e:
            _log_message_.message_handle(
                msg=f"create_session bsky: {e}\n{traceback.format_exc()}",
                level="error",
            )



class PostOnBsky(BaseforBsky):
    def __init__(self, bskyuser):
        super().__init__(bskyuser)

    def tweet(self, tweetcontent, url):
        """
        self.tweetcontent und self.url sind nur relevant, während die tweet()-Methode ausgeführt wird.
        Sie werden nirgendwo außerhalb dieser Methode benötigt.
        """

        tweet_already_existing = BskyDatabase.query.filter_by(url=url).first()
        if tweet_already_existing:
            print("URL bereits gepostet. Kein Tweet gesendet.")
            return

        if not self.session:
            print("Keine Session gefunden. Erstelle automatisch eine neue Session.")
            self.create_session()

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        ### Link-Indexing
        url_match = re.search(r"https?://\S+", tweetcontent)
        if url_match:
            url = url_match.group(0)

        post = {
            "$type": "app.bsky.feed.post",
            "text": tweetcontent,
            "facets": [
            {
                "index": {
                    "byteStart": url_match.start(),
                    "byteEnd": url_match.end()
                },
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": url
                    }
                ]
            }
        ],
            "createdAt": now,
        }

        try:
            resp = requests.post(
                "https://bsky.social/xrpc/com.atproto.repo.createRecord",
                headers={"Authorization": "Bearer " + self.session["accessJwt"]},
                json={
                    "repo": self.session["did"],
                    "collection": "app.bsky.feed.post",
                    "record": post,
                },
            )

            origin_log_msg("Response code: {}".format(resp.status_code))
            resp.raise_for_status()

            ### auskommentieren in Production
            # print(json.dumps(resp.json(), indent=4))

            add_to_db = BskyDatabase(url)
            db.session.add(add_to_db)
            db.session.commit()

        except Exception as e:
            _log_message_.message_handle(
                msg=f"unerwarteter Fehler: {e}",
                level="error",
            )



### INIT INSTANCES
bsky_post_sw = PostOnBsky("sportwetten")
