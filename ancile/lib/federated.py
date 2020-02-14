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
        users = f.read().split('\n')

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
    def __init__(self, app_id=None):
        from queue import Queue
        self.error = None
        self.correlation_ids = set()
        self.request_queue = Queue()
        self.callback_result = None

    def __on_response(self, ch, method, props, body):
        import dill
        import requests
        if (not self.error) and props.correlation_id in self.correlation_ids:            
            self.correlation_ids.remove(props.correlation_id)
            body = requests.get(body).content
            response = dill.loads(body)
            
            if "error" in response:
                self.error = response["error"]
                return
            
            dpp = response["data_policy_pair"]
            self.callback_result = self.callback(initial=self.callback_result, dpp=dpp)

    def send_to_edge(self, model, participant_dpp, program):
        import dill
        target_name = participant_dpp._data["target_name"]
        model._data["model_id"] = participant_dpp._data["model_id"]
        participant_dpp._data = model._data

        participant_dpp = dill.dumps(participant_dpp)
        body = {"program": program, "data_policy_pair": participant_dpp} 
        self.request_queue.put((target_name, body, ))

    def poll_and_process_responses(self, callback):
        import uuid
        import pika
        from ancile.lib.federated_helpers.messaging import send_message

        self.callback = callback

        params = pika.ConnectionParameters(host='localhost',
                                           heartbeat=600,
                                           blocked_connection_timeout=600)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1, global_qos=True)

        while self.request_queue:
            target, body = self.request_queue.get()
            correlation_id = str(uuid.uuid4())
            self.correlation_ids.add(correlation_id)
            
            send_message(target,
                        body,
                        correlation_id,
                        channel,
                        self.__on_response)

        while True:
            connection.process_data_events()
            if self.error:
                raise Exception("Ancile Error")
            if not self.correlation_ids:
                break
            
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
def accumulate(initial, dpp):
    import dill
    import torch
    # averaging part
    incoming_dp = dill.loads(dpp)
    initial = initial or dict()
    counter = initial.pop("counter", 0)
    initial = initial.pop("initial", dict())
    for name, data in incoming_dp.items():
        #### don't scale tied weights:
        if name == 'decoder.weight' or '__' in name:
            continue
        if initial.get(name, False) is False:
            initial[name] = torch.zeros_like(data, requires_grad=True)
        with torch.no_grad():
            initial[name].add_(data)
    return {
        "initial": initial,
        "counter": counter + 1
    }


@TransformDecorator()
def average(accumulated, model, enforce_user_count=0): #summed_dps, global_model, eta, diff_privacy=None, enforce_user_count=0):
    import torch

    eta = 100
    diff_privacy = None
    model = model.get(model, dict())

    if enforce_user_count and enforce_user_count > accumulated.get(counter, 0):
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
