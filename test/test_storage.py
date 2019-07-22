import unittest
import unittest.mock as mock
# from test.tools import run_test
# from ancile_web.errors import ParseError


class StorageTest(unittest.TestCase):
    @mock.patch('redis.StrictRedis.get')
    @mock.patch('redis.StrictRedis.set')
    def test_first(self, mock_set, mock_get):
        from core.core import assemble_locals
        from core.datapolicypair import DataPolicyPair
        from core.result import Result
        # from ancile_core.storage import load
        from core.utils import _decrypt as decrypt

        data = {}
        def m_set(key, value):
            data[key] = value

        def get(key):
            return data[key]

        mock_get.side_effect = get
        mock_set.side_effect = m_set

        local = assemble_locals(Result(), None, -1)
        encrypt = local['encrypt']
        result = local['result']
        load = local['load']

        dp = DataPolicyPair('ANYF*', None, None, None, None)

        dp._data.update(a=5, b="test", c=5, d={"two": "four", "three": "five"})
        self.assertEqual(len(dp._data), 5)
        encrypt(dp, 'dp')
        self.assertEqual(len(dp._data), 0)

        loaded_dp = load(result._stored_keys['dp'])
        self.assertEqual(loaded_dp._encryption_keys, dp._encryption_keys)
        self.assertEqual(len(loaded_dp._data), 0)
        self.assertEqual(len(loaded_dp._encryption_keys), 4)
        self.assertEqual(len(dp._encryption_keys), 4)


        result.append_dp_data_to_result(data=dp, decrypt_field_list=['a', 'b', 'd'])
        self.assertEqual(len(result._dp_pair_data[0]), 3)
        self.assertEqual(len(result._encrypted_data['dp']), 4)

        decrypted_data = decrypt(result._dp_pair_data[0],
                                 result._encrypted_data['dp'])

        self.assertEqual(len(decrypted_data), 3)
        self.assertEqual(decrypted_data['a'], 5)
        self.assertEqual(decrypted_data['b'], "test")
        self.assertEqual(decrypted_data['d'], {"two": "four", "three": "five"})


        with self.assertRaises(KeyError):
            decrypted_data['c']


