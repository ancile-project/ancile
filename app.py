# from src.secret import *
from flask import Flask, request, json, render_template, url_for, Response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required
from flask_security.core import current_user
from flask_security.forms import ConfirmRegisterForm
from flask_principal import Principal, Permission, RoleNeed
from flask_migrate import Migrate
from flask_mail import Mail
from wtforms.fields import SelectMultipleField
import redis
from src.micro_data_core_python.core import execute, UserInfoBundle
import yaml
import traceback
import pickle
import logging
import jwt
import config
from config import REDIS_CONFIG, ENABLE_CACHE

logger = logging.getLogger(__name__)

app = Flask(__name__)
config.configure_app(app)

mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
r = redis.Redis(**REDIS_CONFIG)

from src.db.db import *   # remove circular import
# import oauth (must be after we've defined the app and db)
from src.oauth.oauth import oauth, OAUTH_BACKENDS


# extend registration form to include role field
class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    roles = SelectMultipleField(u'Role', choices=[("user", "User"), ("app", "Application")], default="user")

user_datastore = SQLAlchemyUserDatastore(db, Account, Role)
security = Security(app, user_datastore,
                    confirm_register_form=ExtendedConfirmRegisterForm)
principals = Principal(app)

# define permissions
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(RoleNeed('user'))
app_permission = Permission(RoleNeed('app'))

def _gen_admin(email):
    from datetime import datetime
    import secrets
    passwd = secrets.token_urlsafe()
    user = user_datastore.create_user(email=email, password=passwd)
    user_datastore.add_role_to_user(user, "admin")
    user.confirmed_at = datetime.now()
    db.session.commit()
    return passwd

def get_user(user, app_id, purpose):
    key_string = user + str(app_id) + str(purpose)
    redis_response = r.get(key_string) if ENABLE_CACHE else None

    if redis_response is None:
        user_id = Account.get_id_by_email(user)
        policies = Policy.get_by_user_app_purpose(app_id, user_id, purpose)
        tokens, private_data = OAuth2Token.get_tokens_by_user(user_id)
        bundle = UserInfoBundle(policies=policies,
                                tokens=tokens,
                                username=user,
                                private_data=private_data)

        if ENABLE_CACHE:
            r.set(key_string, pickle.dumps(bundle), ex=3600)
        return bundle
    print("USED CACHED USER")
    return pickle.loads(redis_response)


def get_app_id(token):
    redis_response = r.get(token) if ENABLE_CACHE else None
    if redis_response is None:
        token = jwt.decode(token, app.config["SECRET_KEY"])['salt']
        app_id = Account.get_id_by_token(token)
        if ENABLE_CACHE:
            r.set(token, pickle.dumps(app_id), ex=3600)
        return app_id
    print('USED CACHED APP_ID')
    return pickle.loads(redis_response)


def get_collection_policies(app_id, user_ids):
    return Collection.get_collection_policies(app_id, user_ids)


@app.route('/api/run', methods=['POST'])
def run_api():
    js = request.json
    #print(js)
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
    # print(f'Policies: {policies}, Tokens: {tokens}')
    print(user_info)

    res = execute(user_info=user_info,
                  program=program,
                  persisted_dp_uuid=persisted_dp_uuid,
                  app_id=app_id,
                  purpose=purpose,
                  collection_info=None)
    # print(f'Res: {res}')
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
    return render_template('admin_panel.html',
                           users=Account.get_users(),
                           apps=Account.get_apps(),
                           tokens=OAuth2Token.query.all(),
                           policies=Policy.query.all(),
                           providers=OAUTH_BACKENDS)

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
    token.data = data
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


if __name__ == "__main__":
        app.run(host='0.0.0.0')

