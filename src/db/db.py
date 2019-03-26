# coding: utf-8
from src.app import db, config
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


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

class Account(Base):
    __tablename__ = 'accounts'

    id = db.Column(db.BigInteger, primary_key=True, server_default=db.text("nextval('accounts_id_seq'::regclass)"))
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(255))
    api_token = db.Column(db.String(255))

    @classmethod
    def get_id_by_token(cls, token):
        acc = cls.query.filter_by(api_token=token).first()
        return acc.id

    @classmethod
    def get_id_by_email(cls, email):
        acc = cls.query.filter_by(email=email).first()
        return acc.id


class SchemaMigration(Base):
    __tablename__ = 'schema_migrations'

    version = db.Column(db.BigInteger, primary_key=True)
    inserted_at = db.Column(db.TIMESTAMP())


class Policy(Base):
    __tablename__ = 'policies'

    id = db.Column(db.BigInteger, primary_key=True, server_default=db.text("nextval('policies_id_seq'::regclass)"))
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

    @classmethod
    def get_by_user_app_purpose(cls, app, user, purpose):
        policies = cls.query.filter_by(app_id=app, user_id=user, purpose=purpose)
        policy_dict = dict()
        for policy in policies:
            policy_dict[policy.provider] = policy.policy
        return policy_dict



class UserIdentity(Base):
    __tablename__ = 'user_identities'
    __table_args__ = (
        db.Index('user_identities_uid_provider_index', 'uid', 'provider', unique=True),
    )

    id = db.Column(db.BigInteger, primary_key=True, server_default=db.text("nextval('user_identities_id_seq'::regclass)"))
    provider = db.Column(db.String(255), nullable=False)
    uid = db.Column(db.String(255), nullable=False)
    tokens = db.Column(JSONB(astext_type=db.Text()))
    data = db.Column(JSONB(astext_type=db.Text()))
    user_id = db.Column(db.ForeignKey('accounts.id'))

    user = db.relationship('Account')

    @classmethod
    def get_tokens_by_user(cls, user):
        user = cls.query.filter_by(user_id=user)
        token_dict = dict()
        for token in user:
            token.update_tokens()
            token_dict[token.provider] = token.tokens

        return token_dict


    def update_tokens(self):
        import requests
        import datetime


        expires_in = self.tokens['expires_in']
        current_update= (datetime.datetime.now() - self.updated_at).total_seconds()
        if expires_in - 100 <= current_update:
            url = config[self.provider]['token_url']
            data = {'refresh_token': self.tokens['refresh_token'],
                    'grant_type': 'refresh_token',
                    'client_id': config[self.provider]['client_id'],
                    'client_secret': config[self.provider]['client_secret']}
            res = requests.post(url, data=data)
            if res.status_code == 200:
                print('Success in updating tokens.')
                self.tokens = res.json()
                self.update()
            else:
                raise Exception(f"Couldn't update token: {res.json()}")




