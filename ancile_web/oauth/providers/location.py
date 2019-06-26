from loginpass._core import UserInfo, OAuthBackend

class Location(OAuthBackend):
    OAUTH_TYPE = '2.0'
    OAUTH_NAME = 'location'
    OAUTH_CONFIG = {
        'api_base_url': 'https://campus.cornelltech.io',
        'access_token_url': "https://campus.cornelltech.io/o/token/",
        'authorize_url': "https://campus.cornelltech.io/o/authorize/",
        'client_kwargs': {'scope': 'read'},
    }


    def profile(self, **kwargs):
        return "success"

