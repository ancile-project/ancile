from ancile_web import app
from flask import redirect
from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint, GitHub, Google
from ancile_web.models import OAuth2Token
from ancile_web.oauth.providers import *

oauth = OAuth(app)
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

backend_path = "ancile_web/oauth/providers/"
backend_names = [mod_name for _, mod_name, _ in pkgutil.iter_modules([backend_path])]
OAUTH_BACKENDS = [getattr(importlib.import_module("ancile_web.oauth.providers." + name), name.capitalize()) for name in backend_names]

def register_backend(backend):
    bp = create_flask_blueprint(backend, oauth, handle_authorize)
    app.register_blueprint(bp, url_prefix='/{}'.format(backend.OAUTH_NAME))

# register backends
for backend in OAUTH_BACKENDS:
    register_backend(backend)

