from src.secret import *
from flask import Flask, request, json
from flask_sqlalchemy import SQLAlchemy
from src.db.db import *
from src.micro_data_core_python.core import execute
import redis
import pickle

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
r = redis.Redis(host='localhost', port=6379, db=0)


@app.route('/api/run', methods=['POST'])
def run_api():
    js = request.json
    token = js['token']
    user = js['user']
    purpose = js['purpose']
    program = js['program']
    app_id = Account.get_id_by_token(token)
    user_id = Account.get_id_by_email(user)
    policies = Policy.get_by_user_app_purpose(app_id, user_id, purpose)
    tokens = UserIdentity.get_tokens_by_user(user_id)
    persisted_dp_uuid = js.get('persisted_dp_uuid', None)
    print(f'Policies: {policies}, Tokens: {tokens}')

    res = execute(policies=policies, program=program,
                  sensitive_data=tokens, persisted_dp_uuid=persisted_dp_uuid)
    print(f'Res: {res}')
    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
