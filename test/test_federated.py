import unittest

import yaml
import sys

from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.core.user_secrets import UserSecrets
from ancile.core.decorators import *
from ancile.lib.federated.models.word_model import RNNModel
from ancile.lib.federated.training import *
from ancile.lib.federated.utils.text_helper import TextHelper
from utils.text_load import *
import random
name = 'test_module_name'
import pickle

import time
from datetime import datetime, timedelta

import os
import pandas as pd

from tqdm import tqdm

SLEEP_TIME = 2

def sample(data):
    data['a'] = 0
    return data


@ExternalDecorator(scopes=['location'])
def fetch_data(user):

    return dict()


class FederatedTests(unittest.TestCase):
    corpus = None
    model = None
    helper = None

    def load_data(self):
        # Ideally we would preload each of the files separately, but I think
        # we can assume for now that the data is preprocessed

        # download from here: https://drive.google.com/file/d/1qTfiZP4g2ZPS5zlxU51G-GDCGGr23nvt/view
        self.corpus = load_data('/home/databox/corpus_80000.pt.tar')

    def init_model(self):
        with open('ancile/lib/federated/utils/words.yaml') as f:
            params = yaml.load(f)
        self.helper = TextHelper(params=params, current_time='None',
                                 name='databox', n_tokens=self.corpus.no_tokens)
        self.model = self.helper.create_one_model()

    def test_run_federated(self, output_csv=None):
        # AncileWeb part:

        # init df
        columns = ['Start Time', 'End Time', 'Duration', 'Data Size']
        df = pd.DataFrame(columns=columns)

        print("Loading data...")
        # this is artificial code to preload all the data
        # in real we would load data on each device:
        self.load_data()

        self.init_model()
        print("Parsing data...")
        self.helper.load_data(self.corpus)  # parses data

        print("Training...")
        train_data_total = self.helper.train_data
        self.helper.train_data = None
        self.helper.corpus.test = None
        self.helper.corpus.train = None


        # weight_accumulator = get_weight_accumulator(self.model, self.helper)

        for participant in tqdm(random.sample(range(len(train_data_total)), 100)):
            train_data = train_data_total[participant]

            # pickle data so we can send it over
            params = pickle.dumps({'global_model': self.model.state_dict(),
                                  'model_id': participant, 'train_data': train_data})

            helper_dumps = pickle.dumps(self.helper)

            tqdm.write("Size (in MB) of helper: %f" % (sys.getsizeof(helper_dumps) / 1024.0 / 1024.0))

            # << Evaluation Start >>
            time.sleep(SLEEP_TIME)
            start_time = time.time()

            updated_weights = train_local(helper=self.helper, params=params)

            end_time = time.time()
            time.sleep(SLEEP_TIME)
            # << Evaluation End >>

            model_state_dict = pickle.loads(updated_weights)

            # # averaging part
            # for name, data in model_state_dict.items():
            #     # don't scale tied weights:
            #     if self.helper.params.get('tied', False) and name == 'decoder.weight' or '__' in name:
            #         continue
            #     weight_accumulator[name].add_(data - self.model.state_dict()[name])

            timedelta = float(end_time - start_time)
            tqdm.write('Participant: %s - Training Duration (sec): %.4f - Data Size: %d' % (participant, timedelta, len(train_data)))

            # Add to df
            data = {columns[0]: start_time,
                    columns[1]: end_time,
                    columns[2]: timedelta,
                    columns[3]: len(train_data)}
            df = df.append(pd.Series(data=data, name=participant))

        # apply averaging to the main model
        # self.helper.average_shrink_models(weight_accumulator, self.model, epoch)

        # save to csv
        if output_csv is not None:
            df.to_csv(output_csv)

    def test_run_non_federated(self):

        # Everything except data fetching should run on the AncileWeb
        self.load_data()
        self.init_model()
        self.helper.load_data(self.corpus)

        optimizer = torch.optim.SGD(self.model.parameters(), lr=self.helper.lr,
                                    momentum=self.helper.momentum,
                                    weight_decay=self.helper.decay)
        self.model.train()
        hidden = self.model.init_hidden(self.helper.batch_size)
        for epoch in range(1, 10):
            participants = random.sample(range(0, 79999), 10)
            for participant in participants:

                # this should come from Ancile Core:
                train_data = self.helper.train_data[participant]

                data_iterator = range(0, train_data.size(0) - 1, self.helper.bptt)
                for batch_id, batch in enumerate(data_iterator):
                    print(f'batch {batch_id}')

                    optimizer.zero_grad()
                    data, targets = self.helper.get_batch(train_data, batch,
                                                          evaluation=False)
                    hidden = self.helper.repackage_hidden(hidden)
                    output, hidden = self.model(data, hidden)
                    print('output')
                    loss = criterion(output.view(-1, self.helper.n_tokens), targets)
                    print('loss')
                    loss.backward()
                    print(f'batch_id: {batch_id}')

    def mixed_learning(self):
        # Everything except data fetching should run on the AncileWeb
        self.load_data()
        self.init_model()
        self.helper.load_data(self.corpus)

        optimizer = torch.optim.SGD(self.model.parameters(), lr=self.helper.lr,
                                    momentum=self.helper.momentum,
                                    weight_decay=self.helper.decay)
        self.model.train()
        hidden = self.model.init_hidden(self.helper.batch_size)
        for epoch in range(1, 10):
            participants = random.sample(range(0, 79999), 10)
            for participant in participants:

                # this should come from Ancile Core:
                train_data = self.helper.train_data[participant]
                if participant > 50000:
                    data_iterator = range(0, train_data.size(0) - 1, self.helper.bptt)
                    for batch_id, batch in enumerate(data_iterator):
                        optimizer.zero_grad()
                        data, targets = self.helper.get_batch(train_data, batch,
                                                              evaluation=False)
                        hidden = self.helper.repackage_hidden(hidden)
                        output, hidden = self.model(data, hidden)
                        loss = criterion(output.view(-1, self.helper.n_tokens), targets)

                        loss.backward()
                        print(f'batch_id: {batch_id}')
                else:
                    train_data = self.helper.train_data[participant]

                    # pickle data so we can send it over
                    params = pickle.dumps({'global_model': self.model.state_dict(),
                                           'model_id': participant, 'train_data': train_data})
                    updated_weights = train_local(helper=self.helper, params=params)
                    model_state_dict = pickle.loads(updated_weights)

                    # averaging part
                    for name, data in model_state_dict.items():
                        # don't scale tied weights:
                        if self.helper.params.get('tied', False) and name == 'decoder.weight' or '__' in name:
                            continue
                        weight_accumulator[name].add_(data - self.model.state_dict()[name])
                    print(f'Participant: {participant}')


if __name__ == "__main__":

    print("Process ID: %d" % os.getpid())

    print("Starting in 10 seconds...\n")
    time.sleep(10)

    print("Started at: %s" % (datetime.now()))
    start_time = time.time()

    FederatedTests().test_run_federated(output_csv='evaluation_federated.csv')

    # save and report elapsed time
    elapsed_time = time.time() - start_time
    print("\nSuccess! Duration: %s" % str(timedelta(seconds=int(elapsed_time))))
