import unittest

from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.core.user_secrets import UserSecrets
from ancile.core.decorators import *

name='test_module_name'


@TransformDecorator(scopes=None)
def sample(data):
    data['a'] = 0
    return data


@ExternalDecorator(scopes=['location'])
def fetch_data(user):

    return dict()


class DecoratorsTests(unittest.TestCase):

    def test_transform(self):

        new_dp = DataPolicyPair('ANYF*', None, 'a', 'a', None)
        new_dp._data = dict()
        result = sample(data=new_dp)

        print(result)
        print(result._data)

    def test_external(self):
        user = UserSecrets({'test_module_name': 'fetch_data.sample'},
                           {'test_module_name': {'access_token': ''}},
                           None, username=None, app_id=None)
        dpp = fetch_data(user=user)
        print(dpp, dpp._data)
        dpp2 = sample(data=dpp)
        print(dpp2, dpp2._data)


