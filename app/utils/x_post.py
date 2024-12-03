import json, os
from requests_oauthlib import OAuth1Session
from app.config import BASEDIR
from dotenv import load_dotenv
load_dotenv()

xuser_dict = {
    "bestinpoker": {
        "consumer_key" : os.getenv("XBIP_CONSUMER_KEY"),
        "consumer_secret" : os.getenv("XBIP_CONSUMER_SECRET"),
    }
}

class BaseforX():
    def __init__(self, xuser):
        # Überprüfen, ob xuser existiert
        if xuser not in xuser_dict:
            raise ValueError(f"Unknown xuser: {xuser}")

        self.consumer_key = xuser_dict[xuser]["consumer_key"]
        self.consumer_secret = xuser_dict[xuser]["consumer_secret"]

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

    def authrequest(self, xuser):
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
        token_dir = os.path.join(BASEDIR, "tokens")
        token_filepath = os.path.join(token_dir, f"x-{xuser}.json")
        with open(token_filepath, "w") as token_file:
            json.dump(tokens, token_file)
        print(f"Tokens saved to {token_filepath}")




class PostOnX(BaseforX):
    def __init__(self, xuser):
        super().__init__(xuser)
        pass







#########AUTH
#######################
# Get request token
request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")

# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

tokens = {
    "access_token": access_token,
    "access_token_secret": access_token_secret,
}

# Speichern des Access-Tokens
with open("tokens.json", "w") as token_file:
    json.dump(tokens, token_file)







#########POST
#######################

# Tokens laden
with open("tokens.json", "r") as token_file:
    tokens = json.load(token_file)

access_token = tokens["access_token"]
access_token_secret = tokens["access_token_secret"]

oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

tweetcontent = {"text": "welong musk"}

# Making the request
response = oauth.post(
    "https://api.twitter.com/2/tweets",
    json=tweetcontent,
)

if response.status_code != 201:
    raise Exception(
        "Request returned an error: {} {}".format(response.status_code, response.text)
    )

print("Response code: {}".format(response.status_code))

json_response = response.json()
print(json.dumps(json_response, indent=4, sort_keys=True))