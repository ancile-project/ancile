#from memory_profiler import profile
from ancile.core.decorators import TransformDecorator
name = 'federated'

def new_model(policy):
    from ancile.core.primitives import DataPolicyPair
    import yaml
    from utils.text_load import load_data
    from ancile.lib.federated_helpers.utils.text_helper import TextHelper

    corpus = load_data('corpus_small.pt.tar')
    with open('ancile/lib/federated_helpers/utils/words.yaml') as f:
        params = yaml.load(f)
    helper = TextHelper(params=params, current_time='None',
                        name='databox', n_tokens=50000)
    helper.load_data(corpus=corpus)
    model = helper.create_one_model().state_dict()
    dpp = DataPolicyPair(policy=policy)
    dpp._data = {"model": model, "helper": helper}
    return dpp

def select_users(user_count):
    import random
    from ancile.core.primitives import DataPolicyPair
    policy = "ANYF*"
    dpps = []
    
    with open('users.txt') as f:
        users = [u for u in f.read().split('\n') if u]

    if len(users) < user_count:
        raise Exception("Not enough users")

    sample = random.sample(users, user_count)
    for model_id, target_name in enumerate(sample):

        dpp = DataPolicyPair(policy=policy)
        dpp._data = {
            "target_name": target_name,
            "model_id": model_id
        }

        dpps.append(dpp)
    return dpps


class RemoteClient:
    def __init__(self, callback):
        from queue import Queue
        import pika
        self.callback = callback
        self.error = None
        self.correlation_ids = set()
        self.callback_result = None
        self.time = None
        self.queue = Queue()
        params = pika.ConnectionParameters(host='localhost',
                                           heartbeat=3600,
                                           blocked_connection_timeout=600)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1, global_qos=True)

    def __on_response(self, ch, method, props, body):
        from time import sleep, time
        import dill
        import os
        arrived = time() - self.time
        if (not self.error) and props.correlation_id in self.correlation_ids:            
            self.correlation_ids.remove(props.correlation_id)
            print(props.correlation_id)
            with open(f'/var/www/html/model', 'rb') as f:
               response = dill.load(f)

            if "error" in response:
                self.error = response["error"]
                return

            dpp = response["data_policy_pair"]
            dpp._data = dpp._data["global_model"]
            self.callback_result = self.callback(initial=self.callback_result, dpp=dpp)
            self.__log((self.time, arrived, time()-self.time, bytes.decode(body), ))


    def send_to_edge(self, model, participant_dpp, program):
        from ancile.core.primitives import DataPolicyPair
        from time import time
        self.time = self.time or time()
        dpp_to_send = DataPolicyPair(policy=participant_dpp._policy)
        dpp_to_send._data = {
                "global_model": model._data["model"],
                "helper": model._data["helper"],
                "model_id": participant_dpp._data["model_id"]
                }
        target_name = participant_dpp._data["target_name"]
        body = {"program": program, "data_policy_pair": dpp_to_send}

        self.queue.put((target_name, body,))
    @staticmethod
    def __log(tupl):
        import os

        to_write = []
        if not os.path.isfile('times.csv'):
            to_write.append("initial request,response arrival (in seconds),processing time (in seconds),execution time (in seconds)")
        to_write.append(','.join(map(str,tupl)))
        to_write.append('')
        with open('times.csv', 'a') as f:
            f.write('\n'.join(to_write))

    def poll_and_process_responses(self):
        from time import time
        import uuid
        from ancile.lib.federated_helpers.messaging import send_message

        create = True
        while not self.queue.empty():

            target, body = self.queue.get()
            print(f"queuing {target}")
            correlation_id = str(uuid.uuid4())
            self.correlation_ids.add(correlation_id)
            send_message(target,
                         body,
                         correlation_id,
                         self.channel,
                         self.__on_response,
                         create
                         )
            create = False

        while True:
            try:
                self.connection.process_data_events()
            except (KeyboardInterrupt, SystemExit):
                self.connection.close()
                raise
            except Exception:
                self.connection.close()
                raise

            if self.error:
                self.connection.close()
                raise Exception(self.error)
            if not self.correlation_ids:
                res = self.callback_result
                self.callback_result = None
                return res
                # add timeout
        if self.correlation_ids:
            self.error = "One or more nodes timed out"


@TransformDecorator()
def train_local(model, data_point):
    """
    This part simulates the

    """
    from ancile.lib.federated_helpers.training import _train_local
    model["train_data"] = data_point
    output = _train_local(**model)
    return output


@TransformDecorator()
#@profile
def accumulate(initial, dpp):
    import torch
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.enabled= True
    torch.backends.cudnn.benchmark= True
    # averaging part
    initial = initial or dict()
    counter = initial.pop("counter", 0)
    initial = initial.pop("initial", dict())
    for name, data in dpp.items():
        #### don't scale tied weights:
        if name == 'decoder.weight' or '__' in name:
            continue
        if initial.get(name, False) is False:
            initial[name] = torch.zeros_like(data, requires_grad=True)
        with torch.no_grad():
            initial[name].add_(data)
        del data
    initial["counter"] = counter+1
    initial["initial"] = initial
    return initial


@TransformDecorator()
def average(accumulated, model, enforce_user_count=0): #summed_dps, global_model, eta, diff_privacy=None, enforce_user_count=0):
    import torch

    eta = 100
    diff_privacy = None
    helper = model["helper"]
    model = model["model"]
    accumulated = accumulated or dict()
    if enforce_user_count and enforce_user_count > accumulated.get("counter", 0):
        raise Exception("User count mismatch")

    accumulated = accumulated.get("initial", {})

    for name, data in model.items():
        #### don't scale tied weights:
        if name == 'decoder.weight' or '__' in name:
            continue

        update_per_layer = accumulated[name] * eta
        if diff_privacy:
            noised_layer = torch.cuda.FloatTensor(data.shape).normal_(mean=0, std=diff_privacy['sigma'])
            update_per_layer.add_(noised_layer)
        with torch.no_grad():
            data.add_(update_per_layer)
    return model
