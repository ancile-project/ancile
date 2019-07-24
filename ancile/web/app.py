from flask import Flask, request, json, render_template, url_for, Response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required
from flask_security.core import current_user
from flask_principal import Principal, Permission, RoleNeed
from flask_migrate import Migrate
from flask_mail import Mail
import redis
from ancile.core.core import execute, UserInfoBundle
import yaml
import traceback
import pickle
import logging
import jwt
import config.loader as config_loader
from ancile.web.forms import ExtendedRegisterForm, ExtendedConfirmRegisterForm
from config.loader import REDIS_CONFIG, ENABLE_CACHE, ENABLE_LOGGING

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

from ancile.web import routes, models
from ancile.utils import errors