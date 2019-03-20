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
def hello_world():

    print(request.data)
    request.__hash__()
    redis_object = r.get(request.data)
    # Implemented caching of queries
    if redis_object:
        print("Found existing query")
        [policies, program, tokens, user_id] = pickle.loads(redis_object)
    else:
        js = request.json
        token = js['token']
        user = js['user']
        purpose = js['purpose']
        program = js['program']
        app_id = Account.get_id_by_token(token)
        user_id = Account.get_id_by_email(user)
        policies = Policy.get_by_user_app_purpose(app_id, user_id, purpose)
        tokens = UserIdentity.get_tokens_by_user(user_id)
        print(f'Caching query for app: {app_id}, user: {user_id}, program: {program}, purpose: {purpose}')


        r.set(request.data, pickle.dumps([policies, program, tokens, user_id]), ex=60)


    print(f'Policies: {policies}, Tokens: {tokens}')
    user_state = r.get(user_id)
    if user_state is None:
        user_state = dict()
    else:
        user_state = pickle.loads(user_state)

    res = execute(policies=policies, program=program, sensitive_data=tokens, user_state=user_state)
    if res:
        r.set(user_id, pickle.dumps(user_state))
    print(f'Res: {res}')
    return json.dumps(res)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)