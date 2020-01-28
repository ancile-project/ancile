import unittest

import yaml

from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.core.user_secrets import UserSecrets
from ancile.core.decorators import *
from ancile.lib.federated_helpers.models.word_model import RNNModel
from ancile.lib.federated_helpers.training import *
from ancile.lib.federated_helpers.utils.text_helper import TextHelper
from ancile.lib.federated import *
from utils.text_load import *
import sys
import random
name='test_module_name'
import pickle



@TransformDecorator(scopes=None)
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
        self.corpus = load_data('/Users/ebagdasaryan/Downloads/old_stuff/corpus_80000.pt.tar')
        self.corpus.train = self.corpus.train[:20]

    def init_model(self):
        with open('ancile/lib/federated_helpers/utils/words.yaml') as f:
            params = yaml.load(f)
        self.helper = TextHelper(params=params, current_time='None',
                                 name='databox', n_tokens=self.corpus.no_tokens)
        self.model = self.helper.create_one_model()


    def test_ancile_controlled(self):
        self.load_data()

        self.init_model()
        model = self.model.state_dict()
        self.helper.load_data(self.corpus)  # parses data

        for epoch in range(1, 10):
            participants = random.sample(range(0, 10), 2)
            weight_accumulator = dict()

            for participant in participants:
                ## this should happen on the client
                train_data = self.helper.train_data[participant]
                train_dpp = DataPolicyPair('(_train_local.accumulate* + average*)*')
                train_dpp._data = train_data
                ## client-side

                # pickle data so we can send it over
                data = pickle.dumps({'helper': self.helper,
                                     'global_model': model,
                                     'train_data': train_dpp,
                                     'model_id': participant
                                     })
                updated_weights = train_local(data=data)
                model_state_dict = pickle.loads(updated_weights)
                print('training done')
                weight_accumulator = accumulate(incoming_dp=model_state_dict, summed_dps=weight_accumulator)
                print('acc done')
            model = average(summed_dps=weight_accumulator, global_model=model, eta=100, diff_privacy=None)
            print(f'avg done. policy: {model._policy}')
        return True


    def test_run_federated(self):
        # AncileWeb part:

        # this is artificial code to preload all the data
        # in real we would load data on each device:
        self.load_data()

        self.init_model()
        self.helper.load_data(self.corpus) # parses data

        # this is the main cycle
        for epoch in range(1, 10):
            participants = random.sample(range(0, 79999), 10)
            weight_accumulator = get_weight_accumulator(self.model, self.helper)

            for participant in participants:
                train_data = self.helper.train_data[participant]

                # pickle data so we can send it over
                params = pickle.dumps({'global_model': self.model.state_dict(),
                            'model_id': participant, 'train_data': train_data})
                updated_weights = train_local(helper=self.helper, params=params)
                model_state_dict = pickle.loads(updated_weights)

                # averaging part
                for name, data in model_state_dict.items():
                    #### don't scale tied weights:
                    if self.helper.params.get('tied', False) and name == 'decoder.weight' or '__' in name:
                        continue
                    weight_accumulator[name].add_(data - self.model.state_dict()[name])
                print(f'participant: {participant}')

            # apply averaging to the main model
            helper.average_shrink_models(weight_accumulator, self.model, epoch)


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
                    optimizer.zero_grad()
                    data, targets = self.helper.get_batch(train_data, batch,
                                                     evaluation=False)
                    hidden = self.helper.repackage_hidden(hidden)
                    output, hidden = self.model(data, hidden)
                    loss = criterion(output.view(-1, self.helper.n_tokens), targets)

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
                        #### don't scale tied weights:
                        if self.helper.params.get('tied', False) and name == 'decoder.weight' or '__' in name:
                            continue
                        weight_accumulator[name].add_(data - self.model.state_dict()[name])
                    print(f'participant: {participant}')













