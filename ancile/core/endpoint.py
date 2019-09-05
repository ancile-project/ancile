from ancile.core.core import *
import pika
import dill


def on_request(ch, method, props, body):

    print(" [x] Received message")

    users_secrets, program, app_id, app_module = dill.loads(body)

    res = execute(users_secrets=users_secrets,
                  program=program,
                  app_id=app_id,
                  app_module=app_module)

    print(f'RESULT: {res}')
    res_dill = dill.dumps(res)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                     body=res_dill)
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='rpc_queue')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()
