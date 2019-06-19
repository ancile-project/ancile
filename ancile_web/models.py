# coding: utf-8
from ancile_web import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.attributes import flag_modified
from flask_security import UserMixin,RoleMixin
from flask_security.core import current_user
from datetime import datetime
from bcrypt import gensalt

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
    access_token = db.Column(db.String(256), nullable=False)
    refresh_token = db.Column(db.String(256))
    expires_at = db.Column(db.Integer, default=0)

    private_data = db.Column(JSONB(astext_type=db.Text()))

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


    @classmethod
    def get_tokens_by_user(cls, user):
        user = cls.query.filter_by(user_id=user)
        token_dict = dict()
        data_dict = dict()
        for token in user:
            # token.update_tokens()
            token_dict[token.name] = token.to_token()
            data_dict[token.name] = token.private_data

        return token_dict, data_dict

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
      return True

    @classmethod
    def insert(cls, purpose, policy, active, provider, app, user, creator):
      policy_obj = cls(purpose=purpose,
                          policy=policy,
                          active=active,
                          provider=provider,
                          app_id=Account.get_id_by_email(app),
                          user_id=Account.get_id_by_email(user),
                          creator_id=creator)
      if not policy_obj.validate():
        return False
      policy_obj.add()
      policy_obj.update()
      return True

    @classmethod
    def get_by_user_app_purpose(cls, app, user, purpose):
        policies = cls.query.filter_by(app_id=app, user_id=user, purpose=purpose)
        policy_dict = dict()
        for policy in policies:
            policy_dict[policy.provider] = policy.policy
        return policy_dict


