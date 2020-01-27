import pika
import dill
import ancile
from ancile.core.core import execute
from time import sleep

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
    print("length of response:", str(len(pickled_body)))
    print("returning response:", str(message))

    index = 0
    part_num = 0
    while index < len(pickled_body):
        part_num += 1
        new_index = min(index+5000000, len(pickled_body))
        channel.basic_publish(
                exchange='',
                routing_key='ancile_reply',
                properties=pika.BasicProperties(
                    correlation_id=properties.correlation_id,
                ),
                body=pickled_body[index:new_index])
        print("sent part", str(part_num))
        index = new_index
    channel.basic_publish(
            exchange='',
            routing_key='ancile_reply',
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id,
            ),
            body="")
    print("sent final blank message")

channel.basic_consume(queue='ancile', on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

