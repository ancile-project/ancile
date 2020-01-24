import pika
import dill
import ancile
from ancile.core.core import execute

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='ancile')


def callback(ch, method, properties, body):
    print(" [x] Received message of length {}".format(len(body)))
    request = dill.loads(body)

    dpp = request.get("data_policy_pair")
    program = request.get("program")

    if not dpp:
        message = {"error": "data_policy_pair missing"}
    elif not program:
        message = {"error": "program missing"}
    else:
        res = execute(users_secrets=[],
                        program=program,
                        app_id=None,
                        app_module=None,
                        data_policy_pairs=[dpp])
        if res["result"] == "error":
            message = {"error": res["traceback"]}
        elif not res["data"]:
            message = {"error": "no dpp found"}
        else:
            message = {"data_policy_pair": res["data"][0]}

    pickled_body = dill.dumps(message)
    print("returning response: ", str(message))
    channel.basic_publish(
            exchange='',
            routing_key='ancile_reply',
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id,
            ),
            body=pickled_body[:len(pickled_body) // 2])
    channel.basic_publish(
            exchange='',
            routing_key='ancile_reply',
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id,
            ),
            body=pickled_body[len(pickled_body) // 2:])

channel.basic_consume(queue='ancile', on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

