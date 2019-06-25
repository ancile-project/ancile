from loginpass._core import UserInfo, OAuthBackend


class Rdl(OAuthBackend):
    OAUTH_TYPE = '2.0'
    OAUTH_NAME = 'rdl'
    OAUTH_CONFIG = {
        'api_base_url': 'https://localhost:9980',
        'access_token_url': 'https://localhost:9980/test/oauth/token',
        'authorize_url': 'https://localhost:9980/test/oauth/authorize',
        'client_kwargs': {'scope': 'usage'},
    }


    def profile(self, **kwargs):
        return "success"