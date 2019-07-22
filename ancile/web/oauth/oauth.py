from web.app import app
from flask import redirect
from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint
from web.models import OAuth2Token
from web.oauth.providers import *
from config.loader import PROVIDERS

oauth = OAuth(app, update_token=OAuth2Token.update_token)
# app.config.from_pyfile('config/oauth_config.py')

# how to handle the authorization callback
def handle_authorize(remote, token, user_info):
    if token:
        OAuth2Token(remote.name, token)
        return redirect("/panel")
    else:
      raise Exception("No token supplied.")

import pkgutil
import importlib

# load local providers
backend_path = "ancile_web/oauth/providers/"
backend_names = [mod_name for _, mod_name, _ in pkgutil.iter_modules([backend_path])]
OAUTH_BACKENDS = [getattr(importlib.import_module("ancile_web.oauth.providers." + name), name.capitalize()) for name in backend_names]

# load loginpass providers
loginpass = importlib.import_module("loginpass")
for provider in PROVIDERS:
    OAUTH_BACKENDS.append(getattr(loginpass, provider))

def register_backend(backend):
    bp = create_flask_blueprint(backend, oauth, handle_authorize)
    app.register_blueprint(bp, url_prefix='/{}'.format(backend.OAUTH_NAME))

# register backends
for backend in OAUTH_BACKENDS:
    register_backend(backend)

