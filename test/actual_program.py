import unittest

from ancile_core.collection import Collection
from ancile_core.datapolicypair import DataPolicyPair


class ActualProgramTests(unittest.TestCase):


    def test_collection_add_remove(self):

        dpp = DataPolicyPair('add_to_collection', None, None, None, None,
                 app_id=None)

        collection = Collection()
        print('Collection policy: ', collection.get_collection_policy())
        print('DPP policy: ',dpp._policy._policy)

        print('add to collection')
        collection.add_to_collection(data=dpp)
        print('Collection policy: ', collection.get_collection_policy())
        print('DPP policy: ',dpp._policy._policy)
        print('remove from collection')
        collection.remove_from_collection(data=dpp)
        print('Collection policy: ', collection.get_collection_policy())
        print('DPP policy: ',dpp._policy._policy)

        return True


