from ancile.core.user_secrets import UserSecrets
from ancile.core.primitives.result import Result
from RestrictedPython import safe_builtins
import traceback
import redis
from collections import namedtuple
from config.loader import REDIS_CONFIG
import logging
from ancile.core.context_building import assemble_locals
from ancile.core.advanced.caching import retrieve_compiled
from ancile.core.advanced.storage import Storage
import pika
import dill

logger = logging.getLogger(__name__)

UserInfoBundle = namedtuple("UserInfoBundle", ['username', 'policies',
                                               'tokens', 'private_data'])


def execute(users_specific, program, app_id=None, app_module=None):
    r = redis.Redis(**REDIS_CONFIG)
    storage = Storage(redis_conneciton=r)
    json_output = dict()
    # object to interact with the program
    result = Result()
    # users_specific = dict()
    # for user in user_info:
    #     user_specific = UserSecrets(user.policies, user.tokens,
    #                                 user.private_data,
    #                                 username=user.username,
    #                                 app_id=app_id)
    #     users_specific[user.username] = user_specific

    glbls = {'__builtins__': safe_builtins}
    lcls = assemble_locals(storage=storage, result=result,
                           user_specific=users_specific,
                           app_id=app_id,
                           app_module=app_module)
    try:
        c_program = retrieve_compiled(program, r)
        exec(c_program, glbls, lcls)

    except:
        print(traceback.format_exc())
        json_output = {'result': 'error', 'traceback': traceback.format_exc()}
        return json_output

    json_output['stored_items'] = result._stored_keys
    json_output['encrypted_data'] = result._encrypted_data
    json_output['data'] = result._dp_pair_data
    json_output['result'] = 'ok'
    return json_output


def callback(ch, method, properties, body):
    print(" [x] Received message")

    users_specific, program, app_id, app_module = dill.loads(body)

    res = execute(users_specific=users_specific,
                  program=program,
                  app_id=app_id,
                  app_module=app_module)

    print(f'RESULT: {res}')


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='ancile')
    channel.basic_consume(queue='ancile',
                          auto_ack=True,
                          on_message_callback=callback)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()
