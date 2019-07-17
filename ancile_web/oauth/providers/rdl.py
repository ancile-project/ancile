from loginpass._core import UserInfo, OAuthBackend

# Currently set up with localhost (i.e. RDL running locally).
# Remember that if Ancile and RDL run on localhost there is danger of them overwriting each other's cookies
# To resolve, set one host to localhost and the other to 127.0.0.1 or modify SESSION_COOKIE_NAME

class Rdl(OAuthBackend):
    OAUTH_TYPE = '2.0'
    OAUTH_NAME = 'rdl'
    OAUTH_CONFIG = {
        'api_base_url': 'https://localhost:9980',
        'access_token_url': 'https://localhost:9980/test/oauth/token',
        'authorize_url': 'https://localhost:9980/test/oauth/authorize',
        'client_kwargs': {'scope': 'usage urls youtube_search youtube_watch'},
    }


    def profile(self, **kwargs):
        return "success"