from app import app
from flask import redirect
from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint, GitHub, Google
from src.oauth.cds import CDS
from src.db.db import OAuth2Token

oauth = OAuth(app)
# app.config.from_pyfile('config/oauth_config.py')

# how to handle the authorization callback
def handle_authorize(remote, token, user_info):
    if token:
        OAuth2Token(remote.name, token)
        return redirect("/panel")
    else:
      raise Exception("No token supplied.")

# list backends
OAUTH_BACKENDS = [CDS, GitHub, Google]

# register backends
for backend in OAUTH_BACKENDS:
    bp = create_flask_blueprint(backend, oauth, handle_authorize)
    app.register_blueprint(bp, url_prefix='/{}'.format(backend.OAUTH_NAME))
