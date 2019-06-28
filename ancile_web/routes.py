from ancile_web.app import app
from flask import Flask, request, json, render_template, url_for, Response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required
from flask_security.core import current_user
from flask_principal import Principal, Permission, RoleNeed
from flask_migrate import Migrate
from flask_mail import Mail
import redis
from ancile_core.core import execute, UserInfoBundle
from ancile_core.policy_sly import PolicyParser
import yaml
import traceback
import pickle
import logging
import jwt
from config.loader import REDIS_CONFIG, ENABLE_CACHE
from ancile_web.models import *
from ancile_web.oauth.oauth import oauth, OAUTH_BACKENDS, register_backend
from ancile_web.errors import AncileException
import signal
from ancile_web.utils import reload_server

logger = logging.getLogger(__name__)
r = redis.Redis(**REDIS_CONFIG)


def get_user(user, app_id, purpose):
    key_string = user + ":" + str(app_id) + ":" + str(purpose)
    redis_response = r.get(key_string) if ENABLE_CACHE else None

    if redis_response is None:
        user_id = Account.get_id_by_email(user)
        policies = Policy.get_by_user_app_purpose(app_id, user_id, purpose)
        tokens, private_data = OAuth2Token.get_tokens_by_user(user_id)
        bundle = UserInfoBundle(policies=PolicyParser.parse_policies(policies),
                                tokens=tokens,
                                username=user,
                                private_data=private_data)

        if ENABLE_CACHE:
            r.set(key_string, pickle.dumps(bundle), ex=3600)
            logger.debug(f'Cache miss for user_key: {key_string}')
        return bundle

    info = pickle.loads(redis_response)
    logger.debug(f"Used cached user info: {info}")
    return info


def get_app_id(token):
    redis_response = r.get(token) if ENABLE_CACHE else None
    if redis_response is None:
        salt = jwt.decode(token, app.config["SECRET_KEY"])['salt']
        app_id = Account.get_id_by_token(salt)
        if ENABLE_CACHE:
            r.set(token, pickle.dumps(app_id), ex=3600)
            logger.debug(f'Cache miss for app token: {token}')
        return app_id
    app_id = pickle.loads(redis_response)
    logger.debug(f'Used cached app id: {app_id}')
    return pickle.loads(redis_response)


# define permissions
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(RoleNeed('user'))
app_permission = Permission(RoleNeed('app'))


@app.route('/api/run', methods=['POST'])
def run_api():
    js = request.json
    logger.info(f'Request: {js}')
    token = js['token']
    users = js['users']
    purpose = js['purpose']
    program = js['program']

    try:
        app_id = get_app_id(token)
    except Exception:
            return json.dumps({"result": "error",
                               "traceback": traceback.format_exc()})

    user_info = []

    for user in users:
        try:
            user_info.append(get_user(user, app_id, purpose))
        except Exception:
            return json.dumps({"result": "error",
                               "traceback": traceback.format_exc()})
    persisted_dp_uuid = js.get('persisted_dp_uuid', None)
    logger.debug(f'Passing user_info: {user_info}')

    res = execute(user_info=user_info,
                  program=program,
                  persisted_dp_uuid=persisted_dp_uuid,
                  app_id=app_id,
                  purpose=purpose,
                  collection_info=None)
    logger.info(f'Returning: {res}')
    return json.dumps(res)


# views

@app.route("/")
@app.route("/index")
@app.route("/panel")
def send_to_panel():
    if current_user.has_role("admin"):
        return redirect("/admin")
    elif current_user.has_role("user"):
        return redirect("/user")
    elif current_user.has_role("app"):
        return redirect("/app")
    else:
        return render_template("landing.html")

@app.route("/admin")
@login_required
@admin_permission.require(http_exception=403)
def admin_panel():
    providers=OAUTH_BACKENDS
    ids = [key.replace("_CLIENT_ID", "") for key in app.config.keys() if "CLIENT_ID" in key]
    secrets = [key.replace("_CLIENT_SECRET", "") for key in app.config.keys() if "CLIENT_SECRET" in key]

    providers_missing_info = [provider for provider in providers if
                               ((provider.OAUTH_NAME.upper() not in ids) or 
                                (provider.OAUTH_NAME.upper() not in secrets))]

    return render_template('admin_panel.html',
                           users=Account.get_users(),
                           apps=Account.get_apps(),
                           tokens=OAuth2Token.query.all(),
                           policies=Policy.query.all(),
                           providers=providers,
                           providers_missing_info=providers_missing_info)

@app.route("/admin/edit_provider/<name>")
@login_required
@admin_permission.require(http_exception=403)
def admin_edit_provider(name):
    provider = None

    for backend in OAUTH_BACKENDS:
        if backend.OAUTH_NAME.lower() == name.lower():
            provider = backend

    if provider == None:
        return redirect("/admin")

    return render_template("admin_edit_provider.html", provider=provider)

@app.route("/admin/handle_edit_provider/<name>", methods=["POST"])
@login_required
@admin_permission.require(http_exception=403)
def admin_handle_edit_provider(name):

    id_key = name.upper() + "_CLIENT_ID"
    secret_key = name.upper() + "_CLIENT_SECRET"

    cl_id = request.form.get("idTextarea")
    cl_secret = request.form.get("secretTextarea")
        
    new_entry = {   id_key     : cl_id,
                    secret_key : cl_secret }

    # update environment
    app.config.update(new_entry)

    # update config
    with open("config/oauth.yaml", "r+") as config_stream:
        config = yaml.safe_load(config_stream)
        
        config['secrets'].update(new_entry)

        config_stream.seek(0)
        config_stream.truncate(0)

        yaml.dump(config, config_stream)

    reload_server()

    return redirect("/admin#providers")

@app.route("/admin/add_provider", methods=["POST"])
@login_required
@admin_permission.require(http_exception=403)
def admin_add_provider():
    name = request.form.get("nameInput")
    baseURL = request.form.get("baseURLInput")
    accessURL = request.form.get("accessURLInput")
    authURL = request.form.get("authURLInput")
    scopes = request.form.get("scopeInput")

    provider_class = (
        f"from loginpass._core import UserInfo, OAuthBackend\n"
        f"class {name.capitalize()}(OAuthBackend):\n"
        f"      OAUTH_TYPE = '2.0'\n"
        f"      OAUTH_NAME = '{name.lower()}'\n"
        f"      OAUTH_CONFIG = {{\n"
        f"          'api_base_url': '{baseURL}',\n"
        f"          'access_token_url': '{accessURL}',\n"
        f"          'authorize_url': '{authURL}',\n"
        f"          'client_kwargs': {{'scope': '{scopes}'}},\n"
        f"          }}\n"
        f"      def profile(self, **kwargs):\n"
        f"          return 'success'"
        )
    

    with open("ancile_web/oauth/providers/" + name.lower() + ".py", "w") as class_stream:
        class_stream.write(provider_class) 

    reload_server()
    
    return redirect("/admin")

@app.route("/admin/delete_provider/<name>")
@login_required
@admin_permission.require(http_exception=403)
def admin_delete_provider(name):

    # wipe client id and secret from configs

    id_key = name.upper() + "_CLIENT_ID"
    secret_key = name.upper() + "_CLIENT_SECRET"
    
    app.config.pop(id_key)
    app.config.pop(secret_key)

    # update config
    with open("config/oauth.yaml", "r+") as config_stream:
        config = yaml.safe_load(config_stream)
        
        config_stream.seek(0)
        config_stream.truncate(0)

        config['secrets'].pop(id_key)
        config['secrets'].pop(secret_key)

        yaml.dump(config, config_stream)

    reload_server()

    return redirect("/admin#providers")

@app.route("/admin/add_policy", methods=["POST"])
@login_required
@admin_permission.require(http_exception=403)
def admin_add_policy():
    app = request.form.get("appSelect")
    user = request.form.get("userSelect")
    purpose = request.form.get("purposeTextarea")
    policy = request.form.get("policyTextarea")
    provider = request.form.get("providerSelect")
    active = True if request.form.get("active") == "on" else False
    # validate policy
    if Policy.insert(purpose, policy, active, provider, app, user, current_user.id):
        return redirect("/admin#policies")
    return redirect("/invalid_policy")

@app.route("/admin/view_policy/<id>")
@login_required
@admin_permission.require(http_exception=403)
def admin_view_policy(id):
    policy = Policy.query.filter_by(id=id).first() 
    return render_template("admin_view_policy.html", policy=policy)

@app.route("/admin/edit_policy/<id>")
@login_required
@admin_permission.require(http_exception=403)
def admin_edit_policy(id):
    policy = Policy.query.filter_by(id=id).first()
    default_app = Account.get_email_by_id(policy.app_id)
    default_user = Account.get_email_by_id(policy.user_id)
    default_purpose = policy.purpose
    return render_template("admin_edit_policy.html",
                           users=Account.get_users(),
                           apps=Account.get_apps(),
                           providers=OAUTH_BACKENDS,
                           default_app=default_app,
                           default_user=default_user,
                           default_purpose=policy.purpose,
                           default_policy=policy.policy,
                           default_provider=policy.provider,
                           default_active=policy.active,
                           id=id)

@app.route("/admin/handle_edit_policy/<id>", methods=["POST"])
@login_required
@admin_permission.require(http_exception=403)
def admin_handle_edit_policy(id):
    app = request.form.get("appSelect")
    user = request.form.get("userSelect")
    purpose = request.form.get("purposeTextarea")
    policy_text = request.form.get("policyTextarea")
    provider = request.form.get("providerSelect")
    active = True if request.form.get("active") == "on" else False

    policy = Policy.query.filter_by(id=id).first()

    policy.app_id = Account.get_id_by_email(app)
    policy.user_id = Account.get_id_by_email(user)
    policy.purpose = purpose
    policy.policy = policy_text
    policy.provider = provider
    policy.active = active

    if not policy.validate():
        return render_template("/invalid_policy")

    policy.update()

    return redirect("/admin#policies")

@app.route("/admin/delete_policy/<id>")
@login_required
@admin_permission.require(http_exception=403)
def admin_delete_policy(id):
    Policy.query.filter_by(id=id).first().delete()
    return redirect("/admin#policies")

@app.route("/admin/view_token/<user_id>/<name>")
@login_required
@admin_permission.require(http_exception=403)
def admin_view_token(user_id, name):
    token = OAuth2Token.query.filter_by(name=name, user_id=user_id).first()
    return render_template("admin_view_token.html", token=token)

@app.route("/admin/delete_token/<user_id>/<name>")
@login_required
@admin_permission.require(http_exception=403)
def admin_delete_token(user_id, name):
    OAuth2Token.query.filter_by(user_id=user_id, name=name).first().delete()
    return redirect("/admin#tokens")

@app.route("/admin/delete_account/<id>")
@login_required
@admin_permission.require(http_exception=403)
def admin_delete_account(id):
    Account.query.filter_by(id=id).first().delete()
    return redirect("/admin")

@app.route("/user")
@login_required
@user_permission.require(http_exception=403)
def user_panel():
    # pass the list of tokens that the current user has,
    # and the list that they have not yet authorized
    tokens = [token.name for token in current_user.tokens]
    available = [backend for backend in OAUTH_BACKENDS
                 if backend.OAUTH_NAME not in tokens]
    policies = Policy.query.filter_by(user_id=current_user.id)
    return render_template('user_panel.html', providers=current_user.tokens,
                           available=available, apps=Account.get_apps(),
                           policies=policies)

@app.route("/user/add_policy", methods=["POST"])
@login_required
@user_permission.require(http_exception=403)
def user_add_policy():
    app = request.form.get("appSelect")
    user = current_user.email
    purpose = request.form.get("purposeTextarea")
    policy = request.form.get("policyTextarea")
    provider = request.form.get("providerSelect")
    active = True if request.form.get("active") == "on" else False
    # validate policy
    if Policy.insert(purpose, policy, active, provider, app, user, current_user.id):
        return redirect("/user#policies")
    return redirect("/invalid_policy")

@app.route("/user/view_policy/<id>")
@login_required
@user_permission.require(http_exception=403)
def user_view_policy(id):
    policy = Policy.query.filter_by(id=id).first() 
    return render_template("user_view_policy.html", policy=policy)

@app.route("/user/edit_policy/<id>")
@login_required
@user_permission.require(http_exception=403)
def user_edit_policy(id):
    policy = Policy.query.filter_by(id=id).first()
    default_app = Account.get_email_by_id(policy.app_id)
    default_purpose = policy.purpose
    return render_template("user_edit_policy.html",
                           apps=Account.get_apps(),
                           providers=OAUTH_BACKENDS,
                           default_app=default_app,
                           default_purpose=policy.purpose,
                           default_policy=policy.policy,
                           default_provider=policy.provider,
                           default_active=policy.active,
                           id=id)

@app.route("/user/handle_edit_policy/<id>", methods=["POST"])
@login_required
@user_permission.require(http_exception=403)
def user_handle_edit_policy(id):
    app = request.form.get("appSelect")
    purpose = request.form.get("purposeTextarea")
    policy_text = request.form.get("policyTextarea")
    provider = request.form.get("providerSelect")
    active = True if request.form.get("active") == "on" else False

    policy = Policy.query.filter_by(id=id).first()

    policy.app_id = Account.get_id_by_email(app)
    policy.purpose = purpose
    policy.policy = policy_text
    policy.provider = provider
    policy.active = active

    if not policy.validate():
        return render_template("/invalid_policy")

    policy.update()

    return redirect("/user#policies")

@app.route("/user/delete_policy/<id>")
@login_required
@user_permission.require(http_exception=403)
def user_delete_policy(id):
    policy = Policy.query.filter_by(id=id).first()
    if policy.user_id == current_user.id:
        policy.delete()
    return redirect("/user#policies")

@app.route("/user/view_token/<name>")
@login_required
@user_permission.require(http_exception=403)
def user_view_token(name):
    token = OAuth2Token.query.filter_by(name=name,
                                        user_id=current_user.id).first()
    return render_template("user_view_token.html", token=token)

@app.route("/user/edit_token/<name>")
@login_required
@user_permission.require(http_exception=403)
def user_edit_token(name):
    token = OAuth2Token.query.filter_by(name=name,
                                        user_id=current_user.id).first()
    return render_template("user_edit_token.html", token=token)

@app.route("/user/handle_edit_token/<name>", methods=["POST"])
@login_required
@user_permission.require(http_exception=403)
def user_handle_edit_token(name):
    data = request.form.get("dataTextarea")
    # VALIDATE JSON
    token = OAuth2Token.query.filter_by(name=name,
                                        user_id=current_user.id).first()
    token.private_data = data
    token.update()
    return redirect("/user")

# user delete token
@app.route("/<name>/delete")
@login_required
@user_permission.require(http_exception=403)
def user_delete_token(name):
    for token in current_user.tokens:
        if token.name == name:
            token.delete() 
            break
    return redirect("/user")

@app.route("/app")
@login_required
@app_permission.require(http_exception=403)
def app_panel():
    policies = Policy.query.filter_by(app_id=current_user.id)
    jwt_token = jwt.encode({'salt': current_user.token_salt},
                           app.config["SECRET_KEY"]).decode('ascii')
    return render_template('app_panel.html', policies=policies,
                           jwt_token=jwt_token)

@app.route("/app/view_policy/<id>")
@login_required
@app_permission.require(http_exception=403)
def app_view_policy(id):
    policy = Policy.query.filter_by(id=id).first()
    return render_template("app_view_policy.html", policy=policy)

@app.route('/logout')
@login_required
def logout():
    # Remove the user information from the session
    logout_user()
    return redirect("/")

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html')
