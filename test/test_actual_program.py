import unittest

from ancile_core.collection import Collection
from ancile_core.datapolicypair import DataPolicyPair
from ancile_core.user_specific import UserSpecific


class ActualProgramTests(unittest.TestCase):


    def test_collection_add_remove(self):
        """
        Trying to test that policy on dpp = remove_from_coll(add_to_coll(dpp))

        :return:
        """

        dpp = DataPolicyPair('add_to_collection', None, None, None, None,
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
        collection.remove_from_collection(data=dpp)
        print('Collection policy: ', collection.get_collection_policy())
        print('DPP policy: ',dpp._policy._policy)

        self.assertEqual(policy, dpp._policy._policy)

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
        from ancile_core.functions.indoor_location import preload_location
        from ancile_core.functions.deep_learning import make_dataset, train
        path = '/Users/ebagdasaryan/Documents/development/ancile/location_dump.json'

        user = UserSpecific({'location': 'ANYF*'}, {'location': {'access_token': ''}}, None, username=None, app_id=None)

        collection = preload_location(user=user, path=path)

        lambda_filter = lambda x: x['device_type'] == 'iPhone'
        new_collection = collection.filter(lambda_filter)

        dp_1 = make_dataset(collection=new_collection, batch_size=20)
        print(dp_1)
        result = train(data=dp_1, epochs=1, batch_size=20, bptt=20, lr=2, log_interval=5, clip=0.25)

        print(collection)


