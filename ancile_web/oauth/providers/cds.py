from loginpass._core import UserInfo, OAuthBackend

class Cds(OAuthBackend):
    OAUTH_TYPE = '2.0'
    OAUTH_NAME = 'cds'
    OAUTH_CONFIG = {
        'api_base_url': 'https://campusdataservices.cs.vassar.edu/',
        'access_token_url': 'https://campusdataservices.cs.vassar.edu/oauth/token',
        'authorize_url': 'https://campusdataservices.cs.vassar.edu/oauth/authorize',
        'client_kwargs': {'scope': 'profile'},
    }


    def profile(self, **kwargs):
        return "success"
        '''
        resp = self.get('user', **kwargs)
        resp.raise_for_status()
        data = resp.json()
        params = {
            'sub': str(data['id']),
            'name': data['name'],
            'email': data.get('email'),
            'preferred_username': data['login'],
            'profile': data['html_url'],
            'picture': data['avatar_url'],
            'website': data.get('blog'),
        }
        return UserInfo(params)
        '''
