# coding: utf-8
from ancile_web.app import db, app
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.attributes import flag_modified
from flask_security import UserMixin,RoleMixin
from flask_security.core import current_user
from datetime import datetime
from bcrypt import gensalt
from ancile_core.policy_sly import PolicyParser
from ancile_web.errors import ParseError
from time import time
from ancile_web.errors import AncileException

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    inserted_at = db.Column(db.TIMESTAMP(), default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP(), default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())
    def add(self):
        db.session.add(self)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self):
        db.session.delete(self)
        return db.session.commit()

metadata = Base.metadata

class Role(Base, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

# roles-users relationship
roles_users = db.Table('roles_users',
        db.Column('account_id', db.Integer(), db.ForeignKey('accounts.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

class OAuth2Token(Base):
    __tablename__ = 'tokens'

    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)

    token_type = db.Column(db.String(20))
    access_token = db.Column(db.String(3000), nullable=False)
    refresh_token = db.Column(db.String(3000))
    expires_at = db.Column(db.Integer, default=0)

    private_data = db.Column(JSONB(astext_type=db.Text()), default="{}")

    def __init__(self, name, token_dict):
        print(name, token_dict)
        self.user_id=current_user.id
        self.name=name
        self.token_type=token_dict['token_type']
        self.access_token=token_dict['access_token']
        if ('refresh_token' in token_dict.keys()) and ('expires_at' in token_dict.keys()):
            self.refresh_token=token_dict['refresh_token']
            self.expires_at=token_dict['expires_at']
        # insert into db
        self.add()
        self.update()

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        ) 

    def expiry_date(self):
        return datetime.utcfromtimestamp(self.expires_at).strftime('%Y-%m-%d %H:%M:%S') if self.expires_at else "N/A"

    def user_email(self):
        return Account.query.filter_by(id=self.user_id).first().email

    @property
    def is_expired(self):
        return time() > self.expires_at

    @classmethod
    def get_tokens_by_user(cls, user):
        user = cls.query.filter_by(user_id=user)
        token_dict = dict()
        data_dict = dict()
        for token in user:
            if token.is_expired:
                try:
                    OAuth2Token.update_token(token.name, token)
                except AncileException:
                    pass
            # token.update_tokens()
            token_dict[token.name] = token.to_token()
            data_dict[token.name] = token.private_data

        return token_dict, data_dict

    @staticmethod
    def update_token(name, token):
        import importlib, requests

        provider = getattr(importlib.import_module("ancile_web.oauth.providers." + name), name.capitalize())
        url = provider.OAUTH_CONFIG['access_token_url']
        auth_method = provider.OAUTH_CONFIG['client_kwargs'].get('token_endpoint_auth_method', 'client_secret_basic')

        client_id = app.config[name.upper() + "_CLIENT_ID"]
        client_secret = app.config[name.upper() + "_CLIENT_SECRET"]

        headers = {}

        # Basic Auth (default)
        from base64 import b64encode as encode
        if auth_method == 'client_secret_basic':
            headers = {"Authorization": "basic " + str(encode(bytes(client_id + ":" + client_secret,'utf8')), 'utf-8')} 


        data = {'refresh_token': token.refresh_token,
                'grant_type': 'refresh_token',
                'client_id': client_id,
                'client_secret': client_secret}

        res = requests.post(url, data=data, headers=headers)
        if res.status_code == 200:
            for key in res.json().keys():
                # make sure key is an attribute of token
                if key in dir(token):
                    setattr(token, key, res.json()[key])
            token.update()
            print('Token updated successfully.')
        else:
            raise AncileException(f"Couldn't update token: {res.json()}")

    # @classmethod
    # def get_private_data_by_user(cls, user):
    #     users = cls.query.filter_by(user_id=user)
    #     data_dict = {}
    #     for user_info in users:
    #         data_dict[user_info.name] = user_info.data

    #     return data_dict

class Account(Base, UserMixin):
    __tablename__ = 'accounts'


    id = db.Column(db.BigInteger, primary_key=True) #, server_default=db.text("nextval('accounts_id_seq'::regclass)"))
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255)) # password hash
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('accounts', lazy='dynamic')) # db.Column(db.String(255))
    tokens = db.relationship('OAuth2Token', backref='accounts')
    confirmed_at = db.Column(db.String(255))

    token_salt = db.Column(db.String(64), default=gensalt)
    salt_timestamp = db.Column(db.String(48), default=datetime.now)

    @classmethod
    def get_id_by_token(cls, token):
        acc = cls.query.filter_by(token_salt=token).first()
        return acc.id

    @classmethod
    def get_id_by_email(cls, email):
        acc = cls.query.filter_by(email=email).first()
        return acc.id

    @classmethod
    def get_email_by_id(cls, id):
        acc = cls.query.filter_by(id=id).first()
        if acc != None:
            return acc.email

    @classmethod
    def get_apps(cls):
        return [app for app in cls.query.all() if app.has_role("app")]

    @classmethod
    def get_users(cls):
        return [user for user in cls.query.all() if user.has_role("user")]


class SchemaMigration(Base):
    __tablename__ = 'schema_migrations'

    version = db.Column(db.BigInteger, primary_key=True)
    inserted_at = db.Column(db.TIMESTAMP())


class Policy(Base):
    __tablename__ = 'policies'

    id = db.Column(db.BigInteger, primary_key=True) #, server_default=db.text("nextval('policies_id_seq'::regclass)"))
    purpose = db.Column(db.String(255), server_default=db.text("NULL::character varying"))
    policy = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))
    read_only = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))
    provider = db.Column(db.Text)
    app_id = db.Column(db.ForeignKey('accounts.id'), index=True)
    user_id = db.Column(db.ForeignKey('accounts.id'), index=True)
    creator_id = db.Column(db.ForeignKey('accounts.id'))

    app = db.relationship('Account', primaryjoin='Policy.app_id == Account.id')
    creator = db.relationship('Account', primaryjoin='Policy.creator_id == Account.id')
    user = db.relationship('Account', primaryjoin='Policy.user_id == Account.id')

    def user_email(self):
      return Account.query.filter_by(id=self.user_id).first()

    def app_email(self):
      return Account.query.filter_by(id=self.app_id).first()

    # to be implemented--will attempt to parse policy
    def validate(self):
        try:
            PolicyParser.parse_it(self.policy)
        except ParseError:
            return False
        return True

    @classmethod
    def insert(cls, purpose, policy, active, provider, app, user, creator, readOnly):
      policy_obj = cls(purpose=purpose,
                          policy=policy,
                          active=active,
                          provider=provider,
                          app_id=Account.get_id_by_email(app),
                          user_id=Account.get_id_by_email(user),
                          creator_id=creator,
                          read_only=readOnly)
      if not policy_obj.validate():
        return False
      policy_obj.add()
      policy_obj.update()
      return True

    @classmethod
    def get_by_user_app_purpose(cls, app, user, purpose):
        from ancile_core.policy import Policy
        policies = cls.query.filter_by(app_id=app, user_id=user, purpose=purpose)
        policy_dict = dict()
        for policy in policies:
            policy_dict[policy.provider] = Policy(policy.policy)
        return policy_dict

class Function(Base):
    __tablename__ = 'functions'
    id = db.Column(db.BigInteger, primary_key=True)
    app_id = db.Column(db.ForeignKey('accounts.id'), index=True)
    code = db.Column(db.Text)
    description = db.Column(db.Text)
    name = db.Column(db.String(128))
    approved = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))

    @classmethod
    def get_app_module(cls, app_id):
        funcs = cls.query.filter_by(app_id=app_id, approved=True).all()
        module = '\n'.join((fn.code for fn in funcs))
        return module

class PolicyGroup(Base):
    __tablename__ = 'policy_group'
    app_id = db.Column(db.ForeignKey('accounts.id'), index=True)
    description = db.Column(db.Text)
    name = db.Column(db.Text)

    @classmethod
    def get_id_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

class PredefinedPolicy(Base):
    __tablename__ = 'predefined_policies'

    purpose = db.Column(db.String(255), server_default=db.text("NULL::character varying"))
    policy = db.Column(db.Text)
    provider = db.Column(db.Text)
    app_id = db.Column(db.ForeignKey('accounts.id'), index=True)
    creator_id = db.Column(db.ForeignKey('accounts.id'))
    approved = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))

    group_id = db.Column(db.ForeignKey('policy_group.id'), index=True)

    app = db.relationship('Account', primaryjoin='PredefinedPolicy.app_id == Account.id')
    group = db.relationship('PolicyGroup', primaryjoin='PredefinedPolicy.group_id == PolicyGroup.id')

    def validate(self):
        try:
            PolicyParser.parse_it(self.policy)
        except ParseError:
            return False
        return True

    @classmethod
    def insert(cls, purpose, policy, provider, app, group, creator, approved):
      policy_obj = cls(purpose=purpose,
                          policy=policy,
                          provider=provider,
                          app_id=Account.get_id_by_email(app),
                          group_id=PolicyGroup.get_id_by_name(group),
                          creator_id=creator,
                          approved=approved)
      if not policy_obj.validate():
        return False
      policy_obj.add()
      policy_obj.update()
      return True

