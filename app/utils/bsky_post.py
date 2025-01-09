import os
import re
import requests
import traceback
import base64
import json
from app import db
from app.utils import _log_message_
from datetime import datetime, timezone
from app.utils.helpers import origin_log_msg
from app.database.models import BskyDatabase
from dotenv import load_dotenv

load_dotenv()

bsky_dict = {
    "mybskyacc": {
        "consumer_key": os.getenv("BLUESKYSPORTWETTEN_HANDLE"),
        "consumer_secret": os.getenv("BLUESKYSPORTWETTEN_APP_PASSWORD"),
    }
}


class BaseforBsky:
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
                json={
                    "identifier": self.consumer_key,
                    "password": self.consumer_secret,
                },
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

    def decode_jwt(self, token):
        """Dekodiert das JWT und gibt das Payload zurück."""
        try:
            payload = token.split(".")[
                1
            ]  # JWT besteht aus drei Teilen: Header.Payload.Signature
            padded_payload = payload + "=" * (-len(payload) % 4)  # Base64-Padding fixen
            decoded_bytes = base64.urlsafe_b64decode(padded_payload)
            return json.loads(decoded_bytes)
        except Exception as e:
            _log_message_.message_handle(
                msg=f"Fehler beim Dekodieren des JWT: {e}",
                level="error",
            )
            return None

    def is_session_valid(self):
        """Überprüft, ob der Session-Token noch gültig ist."""
        if not self.session or "accessJwt" not in self.session:
            _log_message_.message_handle(
                msg="Kein gültiger Session-Token vorhanden.", level="warning"
            )
            return False

        token_info = self.decode_jwt(self.session["accessJwt"])
        if not token_info or "exp" not in token_info:
            _log_message_.message_handle(
                msg="Session-Token konnte nicht dekodiert werden.", level="warning"
            )
            return False

        exp_time = datetime.fromtimestamp(token_info["exp"], tz=timezone.utc)
        if exp_time < datetime.now(timezone.utc):
            _log_message_.message_handle(
                msg="Session-Token ist abgelaufen.", level="info"
            )
            return False

        return True

    def ensure_session(self):
        """Stellt sicher, dass eine gültige Session existiert."""
        if not self.is_session_valid():
            _log_message_.message_handle(
                msg="Session ungültig, erstelle neue...", level="info"
            )
            self.create_session()


class PostOnBsky(BaseforBsky):
    def __init__(self, bskyuser):
        super().__init__(bskyuser)

    def tweet(self, tweetcontent, url):
        """
        self.tweetcontent und self.url sind nur relevant, während die tweet()-Methode ausgeführt wird.
        Sie werden nirgendwo außerhalb dieser Methode benötigt.
        """

        ### ist die session noch gültig?
        self.ensure_session()

        tweet_already_existing = BskyDatabase.query.filter_by(url=url).first()
        if tweet_already_existing:
            print("URL bereits gepostet. Kein Tweet gesendet.")
            return

        if not self.session:
            print("Keine Session gefunden. Erstelle automatisch eine neue Session.")
            self.create_session()

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # ### Link-Indexing
        # url_match = re.search(r"https?://\S+", tweetcontent)
        # # Hashtag-Matching
        # hashtag_matches = list(re.finditer(r"#\w+", tweetcontent))

        # URL-Matching
        url_match = re.search(r"https?://[^\s\[\]()<>]+", tweetcontent)
        # Hashtag-Matching
        hashtag_matches = list(re.finditer(r"#\w+", tweetcontent))

        facets = []

        if url_match:
            facets.append(
                {
                    "index": {
                        "byteStart": url_match.start(),
                        "byteEnd": url_match.end(),
                    },
                    "features": [
                        {
                            "$type": "app.bsky.richtext.facet#link",
                            "uri": url_match.group(0),
                        }
                    ],
                }
            )

        for match in hashtag_matches:
            facets.append(
                {
                    "index": {"byteStart": match.start(), "byteEnd": match.end()},
                    "features": [
                        {
                            "$type": "app.bsky.richtext.facet#tag",
                            "tag": match.group(0)[1:],  # Entfernt das "#" für Bluesky
                        }
                    ],
                }
            )

        # Erstelle den Bluesky-Post
        post = {
            "$type": "app.bsky.feed.post",
            "text": tweetcontent,
            "facets": facets,
            "createdAt": now,
        }

        # post = {
        #     "$type": "app.bsky.feed.post",
        #     "text": tweetcontent,
        #     "facets": [
        #         {
        #             "index": {
        #                 "byteStart": url_match.start(),
        #                 "byteEnd": url_match.end(),
        #             },
        #             "features": [
        #                 {
        #                     "$type": "app.bsky.richtext.facet#link",
        #                     "uri": url_match.group(0),
        #                 }
        #             ],
        #         }
        #     ],
        #     "createdAt": now,
        # }

        try:
            if not self.session:
                _log_message_.message_handle(
                    msg="Fehler: Keine gültige Session. Der Post (bsky) wird nicht gesendet.",
                    level="error",
                )
                return

            resp = requests.post(
                "https://bsky.social/xrpc/com.atproto.repo.createRecord",
                headers={"Authorization": "Bearer " + self.session["accessJwt"]},
                json={
                    "repo": self.session["did"],
                    "collection": "app.bsky.feed.post",
                    "record": post,
                },
            )

            origin_log_msg("Response code bsky: {}".format(resp.status_code))
            resp.raise_for_status()

            ### auskommentieren in Production
            # import json
            # print(json.dumps(resp.json(), indent=4))

            add_to_db = BskyDatabase(url)
            db.session.add(add_to_db)
            db.session.commit()

        except Exception as e:
            error_message = (
                f"Unerwarteter Fehler: {e}\nPost-Daten: {json.dumps(post, indent=4)}"
            )

            if "resp" in locals() and resp is not None:  # Falls `resp` existiert
                try:
                    error_message += f"\nResponse TEXT: {resp.text}"
                except Exception as resp_error:
                    error_message += f"\nFehler beim Abrufen der Response: {resp_error}"
            else:
                error_message += "\nKeine Response erhalten."

            _log_message_.message_handle(msg=error_message, level="error")


### INIT INSTANCES
bsky_post_sw = PostOnBsky("mybskyacc")
