import pika
import dill
import ancile
from ancile.core.core import execute
from time import sleep, time
from socket import gethostname
from flask import Flask, request
from multiprocessing import Process
import sys
import requests
import torch

creds = pika.PlainCredentials('test', 'test')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='54.241.202.32', credentials=creds))
channel = connection.channel()
hostname = gethostname() if len(sys.argv) < 2 else sys.argv[1]
url = "http://databox-nuc.dyson.ic.ac.uk"
port = "5672"


def start_server(corr_id, msg, hostname):

    app = Flask(corr_id)

    def handle():
        request.environ.get('werkzeug.server.shutdown')()
        return msg

    app.add_url_rule(f'/{corr_id}', corr_id, handle)

    server = Process(target=app.run, kwargs={"port": port, "host": "0.0.0.0"})
    server.start()
    channel.basic_publish(
            exchange='',
            routing_key=hostname+'_reply',
            properties=pika.BasicProperties(
                correlation_id=corr_id #properties.correlation_id,
            ),
            body=f"{url}:{port}/{corr_id}")
    if not server.join(6000):
        server.terminate()
        server.join()

def callback(hostname):
    def debug(msg):
        print(f"[{hostname}] {msg}")

    def func(ch, method, properties, body):
        debug(f"Received message of length {len(body)}")
        body = requests.get(body).content
        request = dill.loads(body)

        dpp = request.get("data_policy_pair")
        program = request.get("program")

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
            if res["result"] == "error":
                message = {"error": res["traceback"]}
            elif not res["data"]:
                message = {"error": "no dpp found"}
            else:
                message = {"data_policy_pair": res["data"][0], "delta": delta}


        pickled_body = dill.dumps(message)
        debug(f"Length of response: {len(pickled_body)}")
        debug(f"Returning response: {message}")
        start_server(properties.correlation_id, pickled_body, hostname)
    return func

for i in range(1):
    hn = f'{hostname}{i}'
    channel.queue_declare(queue=hn)
    channel.basic_consume(queue=hn, on_message_callback=callback(hn), auto_ack=True)
    print(f'[{hn}] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

