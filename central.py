import pickle
import json
from ancile.core.core import execute
# ML stuff
import yaml
from utils.text_load import load_data
from ancile.lib.federated_helpers.utils.text_helper import TextHelper
import pickle
from ancile.utils.messaging import RpcClient
import dill
from ancile.lib.federated import average

def execute(users):
    remote_program = '''
dpp = data_policy_pairs.pop()
dpp = federated.train_local(data=dpp)
result.return_to_web(dpp=dpp)
    '''

    print("Loading dataset...")
    corpus = load_data('./corpus_80000.pt.tar')
    with open('ancile/lib/federated_helpers/utils/words.yaml') as f:
        params = yaml.load(f)
    helper = TextHelper(params=params, current_time='None',
                        name='databox', n_tokens=corpus.no_tokens)
    model = helper.create_one_model().state_dict()
    helper.load_data(corpus=corpus)
    
    print("Connecting to RMQ server...")
    client = RpcClient(app_id=1)

    for index, user in enumerate(users):
        train_data = helper.train_data[index]


        # backup dataset
        temp_train_data = helper.train_data
        temp_corpus = helper.corpus
        helper.train_data = None
        helper.corpus = None

        data = dill.dumps({
            'helper': helper,
            'global_model': model,
            'model_id': index,
            'train_data': train_data})

        helper.train_data = temp_train_data
        helper.corpus = temp_corpus

        # need to fetch user policy and hostnames
        policy = "train_local.accumulate.average"
        host = "localhost"

        client.queue(user, policy, data, host, remote_program)

    print("Starting loop...")
    client.loop()

    if client.error:
        print("Remote error", client.error)
    else:
        weights = client.weights
        model = average(summed_dps=weights, global_model=model, eta=100, diff_privacy=None)
        print(f'Avg done. policy:', policy)

#execute(["turing", "mote"])
execute(["sp309-17" + str(i) for i in  range(10)])
