from loginpass._core import UserInfo, OAuthBackend
class Test(OAuthBackend):
      OAUTH_TYPE = '2.0'
      OAUTH_NAME = 'test'
      OAUTH_CONFIG = {
          'api_base_url': 'website.com',
          'access_token_url': 'website.com/access',
          'authorize_url': 'website.com/auth',
          'client_kwargs': {'scope': 'profile'},
          }
      def profile(self, **kwargs):
          return 'success'