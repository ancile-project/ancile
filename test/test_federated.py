import unittest

import yaml

from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.core.user_secrets import UserSecrets
from ancile.core.decorators import *
from ancile.lib.federated.models.word_model import RNNModel
from ancile.lib.federated.training import *
from ancile.lib.federated.utils.text_helper import TextHelper
from utils.text_load import *
import random
name='test_module_name'



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

    def test_load_data(self):
        self.corpus = load_data('/Users/ebagdasaryan/Downloads/corpus_80000.pt.tar')

    def init_model(self):
        with open('ancile/lib/federated/utils/words.yaml') as f:
            params = yaml.load(f)
        self.helper = TextHelper(params=params, current_time='None',
                                 name='databox', n_tokens=self.corpus.no_tokens)
        self.model = self.helper.create_one_model()

    def test_run_federated(self):
        self.test_load_data()
        self.init_model()
        self.helper.load_data(self.corpus)

        for epoch in range(1, 10):
            participants = random.sample(range(0, 79999), 10)
            weight_accumulator = get_weight_accumulator(self.model, self.helper)

            for participant in participants:
                train_data = self.helper.train_data[participant]
                model_state_dict = train_local(helper=self.helper, global_model=self.model.state_dict(),
                            model_id=participant, train_data=train_data)
                for name, data in model_state_dict.items():
                    #### don't scale tied weights:
                    if self.helper.params.get('tied', False) and name == 'decoder.weight' or '__' in name:
                        continue
                    weight_accumulator[name].add_(data - self.model.state_dict()[name])
                print(f'participant: {participant}')
            helper.average_shrink_models(weight_accumulator, self.model, epoch)










