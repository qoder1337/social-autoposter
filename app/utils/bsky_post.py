import json, os
import requests
from app import db
from datetime import datetime, timezone
from app.database.models import BskyDatabase

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
        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": self.consumer_key, "password": self.consumer_secret},
        )

        resp.raise_for_status()
        self.session = resp.json()
        print(self.session["accessJwt"])

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

        post = {
            "$type": "app.bsky.feed.post",
            "text": tweetcontent,
            "createdAt": now,
        }

        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": "Bearer " + self.session["accessJwt"]},
            json={
                "repo": self.session["did"],
                "collection": "app.bsky.feed.post",
                "record": post,
            },
        )
        print(json.dumps(resp.json(), indent=2))
        resp.raise_for_status()

        add_to_db = BskyDatabase(url)
        db.session.add(add_to_db)
        db.session.commit()


### INIT INSTANCES
bsky_post_sw = PostOnBsky("sportwetten")
