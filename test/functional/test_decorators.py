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


@TransformDecorator(scopes=None)
def sample3(data_list):
    data = sum(data_list)
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

        new_dp1 = DataPolicyPair('ANYF*.a', None, 'a', 'a', None)
        new_dp1._data = 1
        new_dp2 = DataPolicyPair('ANYF*.a', None, 'a', 'a', None)
        new_dp2._data = 2
        result = sample2(data1=new_dp1, data2=new_dp2)

        self.assertEqual(result._data, {'data1': 1, 'data2': 2})
        print(result._policy)

    def test_transform_param_dpp_list(self):

        new_dp1 = DataPolicyPair('ANYF*.a', None, 'a', 'a', None)
        new_dp1._data = 1
        new_dp2 = DataPolicyPair('ANYF*.a', None, 'a', 'a', None)
        new_dp2._data = 2
        result = sample3(data_list=[new_dp1, new_dp2])

        self.assertEqual(result._data, 3)
        print(result._policy)

    def test_external(self):
        user = UserSecrets({'test_module_name': 'fetch_data.sample'},
                           {'test_module_name': {'access_token': ''}},
                           None, username=None, app_id=None)
        dpp = fetch_data(user=user)
        print(dpp, dpp._data)
        dpp2 = sample(data=dpp)
        print(dpp2, dpp2._data)

    def test_dict_access(self):

        new_dp = DataPolicyPair('ANYF*', None, 'a', 'a', None)
        new_dp._data = {'a': 3}
        result = new_dp['a']

        self.assertEqual(result._data, 3)

    def test_list_access(self):

        new_dp = DataPolicyPair('ANYF*', None, 'a', 'a', None)
        new_dp._data = [0, 1, 2, 3, 4]
        result = new_dp[2]

        self.assertEqual(result._data, 2)



