import os
import dill
import pika

def send_message(target, body, corr_id, channel, callback, create=False):

    url = "http://143.229.6.212"
    port = "80"

    callback_queue = channel.queue_declare(queue=f'{target}_reply', durable=True).method.queue
    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=callback,
        auto_ack=True)
    filename = f'./model'
    if create:
        with open(filename, 'wb') as f:
            dill.dump(body, f)

    channel.basic_publish(
            exchange='',
            routing_key=target,
            properties=pika.BasicProperties(
                correlation_id=corr_id #properties.correlation_id,
            ),
            body=f"{url}:{port}/model")

