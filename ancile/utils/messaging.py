import pika
import dill
import uuid
from time import sleep
from ancile.core.primitives import DataPolicyPair
import json

class RpcClient(object):

    def __init__(self, app_id=None):
        self.app_id = app_id
        self.cor_id_con_map = dict()
        self.responses = list()
        self.error = None

    def on_response(self, ch, method, props, body):
        print("received message: ", body)
        if (not self.error) and props.correlation_id in self.cor_id_con_map:
            connection = self.cor_id_con_map.pop(props.correlation_id)
            print(body)
            response = dill.loads(body)

            if "error" in response:
                self.error = response["error"]
                return

            dp = response["data_policy_pair"]
            self.responses.append(dp)

    def queue(self, user, policy, data, host, program):
        data_policy_pair = DataPolicyPair(policy=policy,
                        username=user,
                        private_data=data,
                        app_id=self.app_id,
                        token=None,
                        name=user)
        
        body = {"program": program, "data_policy_pair": data_policy_pair}
        pickled_body = dill.dumps(body)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        channel = connection.channel()
        result = channel.queue_declare(queue='ancile_reply')
        callback_queue = result.method.queue
        channel.basic_consume(
            queue=callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        
        corr_id = str(uuid.uuid4())
        self.cor_id_con_map[corr_id] = connection
        channel.basic_publish(
            exchange='',
            routing_key='ancile',
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id,
            ),
            body=pickled_body)
    
    def loop(self, time=30):
        for _ in range(time):
            for connection in tuple(self.cor_id_con_map.values()):
                connection.process_data_events()
            if self.error or not self.cor_id_con_map:
                break
            sleep(1)
        if self.cor_id_con_map:
            self.error = "One or more nodes timed out"
