from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_principal import Principal
from flask_migrate import Migrate
from flask_mail import Mail
import logging
import config.loader as config_loader
from ancile.web.forms import ExtendedRegisterForm

logger = logging.getLogger(__name__)

app = Flask(__name__)
config_loader.configure_app(app)

mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from ancile.web.models.models import Account, Role   # remove circular import


user_datastore = SQLAlchemyUserDatastore(db, Account, Role)


security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm,
                    confirm_register_form=ExtendedRegisterForm)
principals = Principal(app)

@security.login_context_processor
def processor():
    return dict(config=app.config)

