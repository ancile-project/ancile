# ML stuff
import yaml
from utils.text_load import load_data
from ancile.lib.federated_helpers.utils.text_helper import TextHelper
from ancile.utils.messaging import RpcClient
import dill
from ancile.lib.federated import average
from random import sample

def execute(users):
    remote_program = '''
model = data_policy_pairs.pop()
reddit_data = databox.get_latest_reddit_data(session="")
trained_model = federated.train_local(model=model, data_point=reddit_data)
result.return_to_web(dpp=trained_model)
    '''

    print("Loading dataset...")
    with open('ancile/lib/federated_helpers/utils/words.yaml') as f:
        params = yaml.load(f)
    helper = TextHelper(params=params, current_time='None',
                        name='databox', n_tokens=50000)
    model = helper.create_one_model().state_dict()
    
    with open("delays.txt") as f:
        delay_list = sample([float(ts) for ts in f.read().split('\n') if ts], len(users))

    print("Connecting to RMQ server...")
    client = RpcClient(app_id=1)

    for index, user in enumerate(users):
        data = dill.dumps({
            'helper': helper,
            'global_model': model,
            'model_id': index})

        # need to fetch user policy and hostnames
        policy = "ANYF*"
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

if __name__ == "__main__":
    import sys
    execute(sys.argv[1:])
