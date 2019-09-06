import unittest

from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.core.user_secrets import UserSecrets
from ancile.core.decorators import *

name='test_module_name'


@TransformDecorator(scopes=None)
def sample(data):
    data['a'] = 0
    return data


@TransformDecorator(scopes=None)
def sample2(data1, data2):
    data = {'data1': data1, 'data2': data2}
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

    def test_transform_multiparam(self):

        new_dp1 = DataPolicyPair('ANYF*', None, 'a', 'a', None)
        new_dp1._data = 1
        new_dp2 = DataPolicyPair('ANYF*', None, 'a', 'a', None)
        new_dp2._data = 2
        result = sample2(data1=new_dp1, data2=new_dp2)

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




