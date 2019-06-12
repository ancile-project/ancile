import unittest
from test.tools import run_test


class FunctionTests(unittest.TestCase):
    def test_simple(self):
        policy = 'test.ret'
        program = ("test(data=dp0);col=Collection()\n"
                   "col.add_to_collection(data=dp0)")
        self.assertFalse(run_test(program, policy))

    def test_simple2(self):
        policy = 'test.add_to_collection'
        program = ("test(data=dp0);col=Collection()\n"
                   "col.add_to_collection(data=dp0)")
        self.assertTrue(run_test(program, policy))

    def test_simple3(self):
        policy0 = 'test.add_to_collection'
        policy1 = 'add_to_collection'
        policy2 = 'test(a=14).add_to_collection'
        program = ("test(data=dp0);col=Collection()\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "test(data=dp2, a=14)\n"
                   "col.add_to_collection(data=dp2)\n")
        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_collection_policy(self):
        policy0 = 'test.add_to_collection'
        policy1 = 'add_to_collection'
        policy2 = 'test(a=14).add_to_collection'
        program = ("test(data=dp0);col=Collection('add_to_collection')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "test(data=dp2, a=14)\n"
                   "col.add_to_collection(data=dp2)\n")
        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_collection_policy2(self):
        policy0 = 'test.add_to_collection'
        policy1 = 'add_to_collection'
        policy2 = 'test(a=14).add_to_collection'
        program = ("test(data=dp0);col=Collection('0')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "test(data=dp2, a=14)\n"
                   "col.add_to_collection(data=dp2)\n")
        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_collection_policy3(self):
        policy0 = 'edit.add_to_collection.collection_sum(value_key="a")'
        policy1 = 'edit.add_to_collection.collection_sum(value_key="a")'
        policy2 = 'edit.add_to_collection.collection_sum(value_key="a")'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('add_to_collection')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_sum(data=col, value_key='a')"
                  )
        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_collection_policy4(self):
        policy0 = 'edit.add_to_collection.collection_sum(value_key="a")'
        policy1 = 'edit.add_to_collection.collection_sum(value_key="a")'
        policy2 = 'edit.add_to_collection.collection_sum(value_key="a")'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('add_to_collection + collection_sum')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_sum(data=col, value_key='a')\n"
                  )
        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_collection_policy5(self):
        policy0 = 'edit.add_to_collection.collection_sum(value_key="a")'
        policy1 = 'edit.add_to_collection.collection_sum(value_key="a")'
        policy2 = 'edit.add_to_collection.collection_sum(value_key="a")'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('add_to_collection + collection_average')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(data=col, value_key='a')\n"
                  )
        with self.assertRaises(ZeroDivisionError):
            run_test(program, policy0, policy1, policy2)

    def test_collection_policy5A(self):
        policy0 = 'edit.add_to_collection.collection_sum(value_key="a")'
        policy1 = 'edit.add_to_collection.collection_sum(value_key="a")'
        policy2 = 'edit.add_to_collection.collection_sum(value_key="a")'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('add_to_collection + collection_average')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(data=col, value_key='a', filter=False)\n"
                  )
        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_collection_policy6(self):
        policy0 = 'edit.add_to_collection.collection_average(value_key="a")'
        policy1 = 'edit.add_to_collection.collection_average(value_key="a")'
        policy2 = 'edit.add_to_collection.collection_average(value_key="a")'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('add_to_collection')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(data=col, value_key='a')\n"
                  )

        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_collection_policy7(self):
        policy0 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        policy1 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        policy2 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('add_to_collection + collection_average')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(data=col, value_key='a')\n"
                  )

        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_collection_policy8(self):
        policy0 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        policy1 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        policy2 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('add_to_collection + collection_average')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(data=col, value_key='a')\n"
                   "test(data=res)\n"
                  )

        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_collection_policy9(self):
        policy0 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        policy1 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        policy2 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('(add_to_collection + collection_average).ret')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(data=col, value_key='a')\n"
                   "ret(data=res)\n"
                  )

        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_collection_policy10(self):
        policy0 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        policy1 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        policy2 = 'edit.add_to_collection.collection_average(value_key="a").ret'
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "edit(data=dp2, key='a', value=5)\n"
                   "col=Collection('(add_to_collection + collection_average)')\n"
                   "col.add_to_collection(data=dp0)\n"
                   "col.add_to_collection(data=dp1)\n"
                   "col.add_to_collection(data=dp2)\n"
                   "res = general.collection_average(data=col, value_key='a')\n"
                   "ret(data=res)\n"
                  )

        self.assertFalse(run_test(program, policy0, policy1, policy2))