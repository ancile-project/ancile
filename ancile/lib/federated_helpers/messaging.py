import pika
from flask import Flask, request
from multiprocessing import Process

def send_message(target, body, corr_id, channel, callback):

    callback_queue = channel.queue_declare(queue=f'{target}_reply').method.queue
    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=callback,
        auto_ack=True)
    
    start_server(corr_id, body, target, channel)

def start_server(corr_id, msg, target, channel):

    url = "http://143.229.6.212"
    port = "8000"
    app = Flask(corr_id)

    def handle():
        request.environ.get('werkzeug.server.shutdown')()
        return msg

    app.add_url_rule(f'/{corr_id}', corr_id, handle)
    server = Process(target=app.run, kwargs={"port": port, "host": "0.0.0.0"})
    server.start()
    channel.queue_declare(queue=target)
    channel.basic_publish(
            exchange='',
            routing_key=target,
            properties=pika.BasicProperties(
                correlation_id=corr_id #properties.correlation_id,
            ),
            body=f"{url}:{port}/{corr_id}")
    if not server.join(6000):
        server.terminate()
        server.join()

