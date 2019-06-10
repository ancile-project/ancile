import unittest
from test.tools import run_test

class FunctionTests(unittest.TestCase):
    def test_reduction_1(self):
        policy0 = 'edit.aggregate_and.ret'
        policy1 = 'edit.aggregate_and.ret'
        policy2 = 'edit.aggregate_and.ret'
        program = ("edit(data=dp0, key='a', value=True)\n"
                   "edit(data=dp1, key='a', value=True)\n"
                   "edit(data=dp2, key='a', value=True)\n"
                   "res = general.aggregate_and(data=[dp0,dp1,dp2], value_keys='a')\n"
                   "ret(data=res)\n"
                  )

        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_reduction_2(self):
        policy0 = 'edit.aggregate_or.ret'
        policy1 = 'edit.aggregate_and.ret'
        policy2 = 'edit.aggregate_and.ret'
        program = ("edit(data=dp0, key='a', value=True)\n"
                   "edit(data=dp1, key='a', value=True)\n"
                   "edit(data=dp2, key='a', value=True)\n"
                   "res = general.aggregate_and(data=[dp0,dp1,dp2], value_keys='a')\n"
                   "ret(data=res)\n"
                  )

        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_reduction_3(self):
        policy0 = 'edit.aggregate_and.ret'
        policy1 = 'edit.aggregate_and.ret'
        policy2 = 'edit.aggregate_and.ret'
        program = ("edit(data=dp0, key='a', value=False)\n"
                   "edit(data=dp1, key='a', value=True)\n"
                   "edit(data=dp2, key='a', value=True)\n"
                   "res = general.aggregate_and(data=[dp0,dp1,dp2], value_keys='a')\n"
                   "ret(data=res)\n"
                  )

        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_reduction_4(self):
        policy0 = 'edit.aggregate_or.ret'
        policy1 = 'edit.aggregate_or.ret'
        policy2 = 'edit.aggregate_or.ret'
        program = ("edit(data=dp0, key='a', value=False)\n"
                   "edit(data=dp1, key='a', value=True)\n"
                   "edit(data=dp2, key='a', value=True)\n"
                   "res = general.aggregate_or(data=[dp0,dp1,dp2], value_keys='a')\n"
                   "ret(data=res)\n"
                  )

        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_basic_1(self):
        policy0 = 'edit.basic_aggregation.ret'
        policy1 = 'edit.basic_aggregation.ret'
        policy2 = 'edit.basic_aggregation.ret'
        program = ("edit(data=dp0, key='a', value=False)\n"
                   "edit(data=dp1, key='a', value=True)\n"
                   "edit(data=dp2, key='a', value=True)\n"
                   "res = general.basic_aggregation(data=[dp0,dp1,dp2])\n"
                   "ret(data=res)\n"
                  )

        self.assertTrue(run_test(program, policy0, policy1, policy2))

    def test_basic_2(self):
        policy0 = 'edit.basic_aggregation.0'
        policy1 = 'edit.basic_aggregation.ret'
        policy2 = 'edit.basic_aggregation.ret'
        program = ("edit(data=dp0, key='a', value=False)\n"
                   "edit(data=dp1, key='a', value=True)\n"
                   "edit(data=dp2, key='a', value=True)\n"
                   "res = general.basic_aggregation(data=[dp0,dp1,dp2])\n"
                   "ret(data=res)\n"
                  )

        self.assertFalse(run_test(program, policy0, policy1, policy2))

    def test_basic_3(self):
        policy0 = 'edit.basic_aggregation.ret'
        policy1 = 'edit.test.ret'
        policy2 = 'edit.basic_aggregation.ret'
        program = ("edit(data=dp0, key='a', value=False)\n"
                   "edit(data=dp1, key='a', value=True)\n"
                   "edit(data=dp2, key='a', value=True)\n"
                   "res = general.basic_aggregation(data=[dp0,dp1,dp2])\n"
                   "ret(data=res)\n"
                  )

        self.assertFalse(run_test(program, policy0, policy1, policy2))