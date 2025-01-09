import os
import json
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session

from app import db
from app.config import BASEDIR
from app.utils import _log_message_
from app.utils.helpers import origin_log_msg
from app.database.models import TweetDatabase


load_dotenv()

xuser_dict = {
    "myxacc": {
        "consumer_key": os.getenv("XBIP_CONSUMER_KEY"),
        "consumer_secret": os.getenv("XBIP_CONSUMER_SECRET"),
    }
}


class BaseforX:
    def __init__(self, xuser):
        # Überprüfen, ob xuser existiert
        if xuser not in xuser_dict:
            raise ValueError(f"Unknown xuser: {xuser}")

        self.consumer_key = xuser_dict[xuser]["consumer_key"]
        self.consumer_secret = xuser_dict[xuser]["consumer_secret"]

        self.token_dir = os.path.join(BASEDIR, "tokens")
        self.token_filepath = os.path.join(self.token_dir, f"x-{xuser}.json")

    def create_session(self, resource_owner_key, resource_owner_secret, verifier=None):
        """Erstellt eine OAuth1Session."""
        return OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )


class AuthorizeOnX(BaseforX):
    def __init__(self, xuser):
        super().__init__(xuser)

    def authrequest(self):
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError as e:
            print("Error fetching request token:", str(e))
            return

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token: %s" % resource_owner_key)

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: %s" % authorization_url)
        verifier = input("Paste the PIN here: ")

        # access token holen
        access_token_url = "https://api.twitter.com/oauth/access_token"

        oauth = self.create_session(resource_owner_key, resource_owner_secret, verifier)
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        tokens = {
            "access_token": access_token,
            "access_token_secret": access_token_secret,
        }

        # Speichern des Access-Tokens

        with open(self.token_filepath, "w") as token_file:
            json.dump(tokens, token_file)
        print(f"Token gespeichert in {self.token_filepath}")


class PostOnX(BaseforX):
    def __init__(self, xuser):
        super().__init__(xuser)

    def tweet(self, tweetcontent, url):
        tweet_already_existing = TweetDatabase.query.filter_by(url=url).first()
        if tweet_already_existing:
            print("URL bereits gepostet. Kein Tweet gesendet.")
            return

        # Tokens laden
        with open(self.token_filepath, "r") as token_file:
            tokens = json.load(token_file)
        access_token = tokens["access_token"]
        access_token_secret = tokens["access_token_secret"]

        oauth = self.create_session(access_token, access_token_secret)

        tweet = {"text": tweetcontent}

        try:
            response = oauth.post(
                "https://api.twitter.com/2/tweets",
                json=tweet,
            )

            if response.status_code != 201:
                _log_message_.message_handle(
                    msg=f"Request Fehler: {response.status_code} {response.text} {response.headers}",
                    level="error",
                )
                return

            origin_log_msg("Response code twitter: {}".format(response.status_code))
            response.raise_for_status()

            # ### auskommentieren in Production
            # print(json.dumps(response.json(), indent=4))

            add_to_db = TweetDatabase(url)
            db.session.add(add_to_db)
            db.session.commit()

        except Exception as e:
            _log_message_.message_handle(
                msg=f"unerwarteter Fehler: {e}",
                level="error",
            )


### INIT INSTANCES
x_post_bip = PostOnX("myxacc")
