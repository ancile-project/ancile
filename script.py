import pika
import dill
import ancile
from ancile.core import execute

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='ancile')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    request = dill.loads(body)

    error = None
    dpp = request.get("data_policy_pair")
    program = request.get("program")
    

channel.basic_consume(queue='ancile', on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

