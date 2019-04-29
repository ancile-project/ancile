from src.secret import *
from flask import Flask, request, json
from flask_sqlalchemy import SQLAlchemy
import redis
from src.micro_data_core_python.core import execute, UserInfoBundle
import yaml
import traceback
import pickle
import logging
from src import logger_setup

logger = logging.getLogger('primary')

with open('./config/secret.yaml', 'r') as f:
    config = yaml.load(f)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
r = redis.Redis(host='localhost', port=6379, db=1)

from src.db.db import *   # remove circular import 


def get_user(user, app_id, purpose):
    key_string = user + str(app_id) + str(purpose)
    redis_response = r.get(key_string)

    if redis_response is None:
        user_id = Account.get_id_by_email(user)
        policies = Policy.get_by_user_app_purpose(app_id, user_id, purpose)
        tokens = UserIdentity.get_tokens_by_user(user_id)
        private_data = UserIdentity.get_private_data_by_user(user_id)
        bundle=UserInfoBundle(policies=policies,
                              tokens=tokens,
                              username=user,
                              private_data=private_data)

        r.set(key_string, pickle.dumps(bundle), ex=3600)
        return bundle
    print("USED CACHED USER")
    return pickle.loads(redis_response)


def get_app_id(token):
    redis_response = r.get(token)
    if redis_response is None:
        app_id = Account.get_id_by_token(token)
        r.set(token, pickle.dumps(app_id), ex=3600)
        return app_id
    print('USED CACHED APP_ID')
    return pickle.loads(redis_response)


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
            return json.dumps({"result": "error", "traceback": traceback.format_exc()})
    persisted_dp_uuid = js.get('persisted_dp_uuid', None)
    #print(f'Policies: {policies}, Tokens: {tokens}')
    #print(user_info)

    res = execute(user_info=user_info, program=program, 
                    persisted_dp_uuid=persisted_dp_uuid, app_id=app_id,
                    purpose=purpose)
    # print(f'Res: {res}')
    return json.dumps(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=True)

