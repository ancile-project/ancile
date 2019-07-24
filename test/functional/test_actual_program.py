import unittest

from ancile.core.primitives.collection import Collection
from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.core.user_secrets import UserSecrets


class ActualProgramTests(unittest.TestCase):


    def test_collection_add_remove(self):
        """
        Trying to test that policy on dpp = remove_from_coll(add_to_coll(dpp))

        :return:
        """

        dpp = DataPolicyPair('add_to_collection.remove_from_collection', None, None, None, None,
                 app_id=None)

        policy = dpp._policy._policy

        collection = Collection()
        print('Collection policy: ', collection.get_collection_policy())
        print('DPP policy: ',dpp._policy._policy)

        print('add to collection')
        collection.add_to_collection(data=dpp)
        print('Collection policy: ', collection.get_collection_policy())
        print('DPP policy: ',dpp._policy._policy)
        self.assertNotEqual(policy, dpp._policy._policy)

        print('remove from collection')
        collection.remove_from_collection(index=0)
        print('Collection policy: ', collection.get_collection_policy())
        print('DPP policy: ',dpp._policy._policy)

        self.assertEqual(1, dpp._policy._policy)

        return True

    def test_collection_add_filter(self):
        """
        Trying to test that policy on dpp = remove_from_coll(add_to_coll(dpp))

        :return:
        """

        dpp_1 = DataPolicyPair('ANYF*', None, None, None, None,
                 app_id=None)
        dpp_1._data = {'val':0}
        dpp_2 = DataPolicyPair('ANYF*', None, None, None, None,
                             app_id=None)
        dpp_2._data = {'val': 10}

        collection = Collection()

        print('add to collection')
        collection.add_to_collection(data=dpp_1)
        collection.add_to_collection(data=dpp_2)

        lambda_function = lambda x: x['val']>6
        collection.filter(lambda_function)
        print(len(collection._data_points))


        return True


    def test_user(self):
        from ancile.lib.indoor_location import preload_location
        from ancile.lib.deep_learning import make_dataset, train, serve_model
        path = '/Users/ebagdasaryan/Documents/development/ancile/location_dump.json'

        user = UserSecrets({'location': 'ANYF*'}, {'location': {'access_token': ''}}, None, username=None, app_id=None)

        collection = preload_location(user=user, path=path)

        lambda_filter = lambda x: x['device_type'] == 'iPhone'
        new_collection = collection.filter(lambda_filter)

        # dp_1 = make_dataset(collection=new_collection, batch_size=20)
        # print(dp_1)
        model = train(collection=new_collection, epochs=1, batch_size=20, bptt=20, lr=2, log_interval=5, clip=0.25)
        result = serve_model( data=[new_collection, model], bptt=20, batch_size=20, value_keys='model')
        print(result._data)


    def test_collection_for_each(self):
        from ancile.lib.general import double
        from ancile.lib.general import collection_average, collection_sum
        from copy import deepcopy
        col = Collection()
        dpp_1 = DataPolicyPair('(collection_average + (double.collection_average)).ret', None, None, None, None,
                                app_id=None)
        dpp_1._data['b'] = 4

        col._data_points = [dpp_1, deepcopy(dpp_1), deepcopy(dpp_1)]

        # print(dpp_1._policy)
        # print(col)
        # print([data._data for data in col._data_points])
        res = collection_average(collection=col, value_key='b')
        self.assertEqual(res._data['collection_average'], 4)
        # print(res._data)
        # print(col)
        # print(dpp_1._policy)
        # print([data._data for data in col._data_points])

        col2 = col.for_each(double, key='b')
        # print([data._data for data in col2._data_points])
        # print(col2)
        res2 = collection_average(collection=col2, value_key='b')
        self.assertEqual(res2._data['collection_average'], 8)
        # print(res2._data)


