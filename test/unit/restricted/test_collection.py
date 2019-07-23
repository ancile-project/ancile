import unittest
from test.unit.restricted.tools import run_test


class CollectionTests(unittest.TestCase):
    def test_simple(self):
        policy = 'test.ret'
        program = ("test(data=dp0);col=Collection()\n"
                   "col.add_to_collection(data=dp0)")
        self.assertFalse(run_test(program, policy))

    def test_simple2(self):
        policy = 'test.add_to_collection'
        program = ("dp0 = test(data=dp0);col=Collection()\n"
                   "col.add_to_collection(data=dp0)")
        self.assertTrue(run_test(program, policy))

    def test_simple3(self):
        policy0 = 'test.add_to_collection*'
        policy1 = 'add_to_collection*'
        policy2 = 'test(a=14).add_to_collection'
        program = ("dp0= test(data=dp0);col=Collection()\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "dp2 = test(data=dp2, a=14)\n"
                   "col.add_to_collection(data=dp2)\n")
        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_collection_policy(self):
        policy0 = 'test.add_to_collection*'
        policy1 = 'add_to_collection*'
        policy2 = 'test(a=14).add_to_collection*'
        program = ("dp0 = test(data=dp0);col=Collection()\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "dp2 = test(data=dp2, a=14)\n"
                   "col.add_to_collection(data=dp2)\n")
        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_collection_policy2(self):
        policy0 = 'test.add_to_collection*'
        policy1 = 'add_to_collection'
        policy2 = 'test(a=14).add_to_collection'
        program = ("dp0 = test(data=dp0);col=Collection()\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "dp2 = test(data=dp2, a=14)\n"
                   "col.add_to_collection(data=dp2)\n")
        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_collection_policy3(self):
        policy0 = 'edit.add_to_collection*.collection_sum(value_key="a")'
        policy1 = 'edit.add_to_collection*.collection_sum(value_key="a")'
        policy2 = 'edit.add_to_collection*.collection_sum(value_key="a")'
        program = ("dp0 = edit(data=dp0, key='a', value=4)\n"
                   "dp1 = edit(data=dp1, key='a', value=4)\n"
                   "dp2 = edit(data=dp2, key='a', value=5)\n"
                   "col=Collection()\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_sum(collection=col, value_key='a')"
                  )
        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_collection_policy5(self):
        policy0 = 'edit.add_to_collection*.collection_sum(value_key="b")'
        policy1 = 'edit.add_to_collection*.collection_sum(value_key="b")'
        policy2 = 'edit.add_to_collection*.collection_sum(value_key="b")'
        program = ("dp0 = edit(data=dp0, key='a', value=4)\n"
                   "dp1 = edit(data=dp1, key='a', value=4)\n"
                   "dp2 = edit(data=dp2, key='a', value=5)\n"
                   "col=Collection()\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(collection=col, value_key='a')\n"
                  )
        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_collection_policy11(self):
        policy0 = 'edit.add_to_collection*.(collection_average + (double.collection_average)).ret'
        policy1 = 'edit.add_to_collection*.(collection_average + (double.collection_average)).ret'
        policy2 = 'edit.add_to_collection*.(collection_average + (double.collection_average)).ret'
        program = ("dp0 = edit(data=dp0, key='a', value=4)\n"
                   "dp1 = edit(data=dp1, key='a', value=4)\n"
                   "dp2 = edit(data=dp2, key='a', value=4)\n"
                   "col=Collection()\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(collection=col, value_key='a')\n"
                   "col2 = col.for_each(double, key='a')\n"
                   "res2 = general.collection_average(collection=col2, value_key='a')\n"
                   "ret(data=res)\n"
                   "ret(data=res2)\n"
                  )

        self.assertTrue(run_test(program, policy0, policy1, policy2))