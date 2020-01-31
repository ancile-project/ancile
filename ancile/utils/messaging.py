import pika
import dill
import uuid
from time import sleep, time
from ancile.core.primitives import DataPolicyPair
import json
import pickle
from ancile.lib.federated import accumulate

from statistics import mean

def debug(user, msg):
    print(f"[{user}] {msg}")

class RpcClient(object):

    def __init__(self, app_id=None):
        self.app_id = app_id
        self.cor_id_con_map = dict()
        self.responses = list()
        self.resp_parts = dict()
        self.error = None
        self.weights = dict()
        self.times = list()
        self.delays = dict()

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", heartbeat=600, blocked_connection_timeout=600))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1, global_qos=True)

        self.begin_time = time()
    def on_response(self, ch, method, props, body):
        print("Received message")
        if (not self.error) and props.correlation_id in self.cor_id_con_map:
            user = self.cor_id_con_map[props.correlation_id]
            
            if body:
                self.resp_parts[props.correlation_id] = self.resp_parts.get(props.correlation_id, b"") + body
                debug(user, "Part processed")
                return
            body = self.resp_parts.pop(props.correlation_id)
            self.cor_id_con_map.pop(props.correlation_id)
            debug(user, "Starting loading")
            response = dill.loads(body)
            debug(user, "Loading done")
            
            if "error" in response:
                debug(user, response["error"])
                self.error = response["error"]
                return
            
            debug(user, "Accumulating")
            dp = response["data_policy_pair"]
            self.weights = accumulate(incoming_dp=dp, summed_dps=self.weights)
            debug(user, "Done accumulating")
            debug(user, "Model processed")
            self.times.append((user, self.delays[user], time()-self.begin_time, ))

    def queue(self, user, policy, data, host, program, delay):
        debug(user, "Queuing model")
        data_policy_pair = DataPolicyPair(policy=policy,
                        username=user,
                        app_id=self.app_id,
                        token=None,
                        name=user)
        data_policy_pair._data = data
        
        body = {"program": program, "data_policy_pair": data_policy_pair, "delay": delay}
        pickled_body = dill.dumps(body)
        
        result = self.channel.queue_declare(queue=user+'_reply')
        callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

         
        corr_id = str(uuid.uuid4())
        self.cor_id_con_map[corr_id] = user
        self.delays[user] = delay
        self.channel.basic_publish(
            exchange='',
            routing_key=user,
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id,
            ),
            body=pickled_body)
    
    def loop(self):
        while True:
            self.connection.process_data_events()
            if self.error or not self.cor_id_con_map:
                with open('times.log', 'a') as f:
                    f.write(str(self.times)+"\n")
                break
        if self.cor_id_con_map:
            self.error = "One or more nodes timed out"
