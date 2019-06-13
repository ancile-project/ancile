# coding: utf-8
from app import db, config
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.attributes import flag_modified

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

    @classmethod
    def get_private_data_by_user(cls, user):
        users = cls.query.filter_by(user_id=user)
        data_dict = {}
        for user_info in users:
            data_dict[user_info.provider] = user_info.data

        return data_dict

    def update_tokens(self):
        import requests
        import datetime
        from base64 import b64encode as encode


        expires_in = int(self.tokens['expires_in'])
        current_update= (datetime.datetime.utcnow() - self.updated_at).total_seconds()
        if expires_in - 100 <= current_update:
            url = config[self.provider]['token_url']
            client_id = config[self.provider]['client_id']
            client_secret = config[self.provider]['client_secret']
            headers = {}
            if config[self.provider].get('basic_auth', False):
                headers = {"Authorization": "basic " + str(encode(bytes(client_id + ":" + client_secret,'utf8')), 'utf-8')} 

            data = {'refresh_token': self.tokens['refresh_token'],
                    'grant_type': 'refresh_token',
                    'client_id': config[self.provider]['client_id'],
                    'client_secret': config[self.provider]['client_secret']}
            res = requests.post(url, data=data, headers=headers)
            if res.status_code == 200:
                print('Success in updating tokens.')
                self.tokens.update(res.json())
                flag_modified(self, "tokens") # make sure changes
                self.update()
            else:
                raise Exception(f"Couldn't update token: {res.json()}")


class Collection(Base):
    __tablename__ = "collections"

    id = db.Column(db.BigInteger, primary_key=True)
    user_ids = db.Column(db.ARRAY(db.Integer))
    app_id = db.Column(db.ForeignKey('accounts.id'))
    policy = db.Column(db.Text)

    active = db.Column(db.Boolean())

    def user_emails(self):
        users = [Account.query.filter_by(id=user_id).first() for user_id in self.user_ids]
        return [user.email for user in users if user != None]

    # parse policy
    def validate(self):
        return True

    def app_email(self):
        return Account.query.filter_by(id=self.app_id).first().email

    @classmethod
    def insert(cls, policy, active, app, users):
        print(users)
        coll_obj = cls(policy=policy,
                       active=active,
                       app_id=Account.get_id_by_email(app),
                       user_ids=[Account.get_id_by_email(user) for user in users])
        if not coll_obj.validate():
            return False
        coll_obj.add()
        coll_obj.update()
        return True

    # THIS IS A STUB
    @classmethod
    def get_collection_policies(cls, app_id, user_ids):
        return cls.query.filter_by(app_id=app_id)\
                  .filter(all(usr in Collection.user_ids for usr in user_ids))\
                  .all()
