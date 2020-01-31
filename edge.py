import pika
import dill
import ancile
from ancile.core.core import execute
from time import sleep, time
from socket import gethostname

creds = pika.PlainCredentials('test', 'test')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='143.229.6.212', credentials=creds))
channel = connection.channel()
hostname = gethostname()
channel.queue_declare(queue=hostname)

def debug(msg):
    print(f"[{hostname}] {msg}")

def callback(ch, method, properties, body):
    debug(f"Received message of length {len(body)}")
    request = dill.loads(body)

    dpp = request.get("data_policy_pair")
    program = request.get("program")
    delay = request.get("delay")

    sleep(delay)

    if not dpp:
        message = {"error": "data_policy_pair missing"}
    elif not program:
        message = {"error": "program missing"}
    else:
        initial = time()
        res = execute(users_secrets=[],
                        program=program,
                        app_id=None,
                        app_module=None,
                        data_policy_pairs=[dpp])
        delta = time() - initial
        with open(hostname+'-delta.log', 'a') as f:
            f.write(str(delta)+'\n')
        if res["result"] == "error":
            message = {"error": res["traceback"]}
        elif not res["data"]:
            message = {"error": "no dpp found"}
        else:
            message = {"data_policy_pair": res["data"][0]}

    pickled_body = dill.dumps(message)
    debug(f"Length of response: {len(pickled_body)}")
    debug(f"Returning response: {message}")

    index = 0
    part_num = 0
    while index < len(pickled_body):
        part_num += 1
        new_index = min(index+100000000, len(pickled_body))
        channel.basic_publish(
                exchange='',
                routing_key=hostname+'_reply',
                properties=pika.BasicProperties(
                    correlation_id=properties.correlation_id,
                ),
                body=pickled_body[index:new_index])
        debug(f"Sent part {part_num}")
        index = new_index
    channel.basic_publish(
            exchange='',
            routing_key=hostname+'_reply',
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id,
            ),
            body="")
    debug("Sent final blank message")

channel.basic_consume(queue=hostname, on_message_callback=callback, auto_ack=True)
debug('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

