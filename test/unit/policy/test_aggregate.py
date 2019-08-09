import unittest

from ancile.core.primitives.policy_helpers.expressions import *
from ancile.lib import general
from ancile.utils.errors import ParseError
from ancile.core.primitives import DataPolicyPair, Policy
from ancile.core.primitives import *
from test.unit.restricted.tools import *
import logging

from test.unit.restricted.tools import display, ret

logger = logging.getLogger(__name__)


class AggregateTest(unittest.TestCase):

    def test_reduction_1(self):
        dp0 = get_dummy_pair('edit.aggregate_and.ret', 0 )
        dp1 = get_dummy_pair('edit.aggregate_and.ret', 1)
        dp2 = get_dummy_pair('edit.aggregate_and.ret', 2)

        dp0 = edit(data=dp0, key='a', value=True)
        dp1 = edit(data=dp1, key='a', value=True)
        dp2 = edit(data=dp2, key='a', value=True)
        res = general.aggregate_and(data=[dp0,dp1,dp2], value_keys='a')
        result = ret(data=res)

        self.assertTrue(result, {'aggregate_and': True})

    def test_reduction_2(self):
        dp0 = get_dummy_pair('edit.aggregate_or.ret', 0 )
        dp1 = get_dummy_pair('edit.aggregate_and.ret', 1)
        dp2 = get_dummy_pair('edit.aggregate_and.ret', 2)

        dp0 = edit(data=dp0, key='a', value=True)
        dp1 = edit(data=dp1, key='a', value=True)
        dp2 = edit(data=dp2, key='a', value=True)

        with self.assertRaises(PolicyError):
            res = general.aggregate_and(data=[dp0, dp1, dp2], value_keys='a')

    def test_reduction_3(self):
        dp0 = get_dummy_pair('edit.aggregate_and.ret', 0)
        dp1 = get_dummy_pair('edit.aggregate_and.ret', 1)
        dp2 = get_dummy_pair('edit.aggregate_and.ret', 2)

        dp0 = edit(data=dp0, key='a', value=False)
        dp1 = edit(data=dp1, key='a', value=True)
        dp2 = edit(data=dp2, key='a', value=True)
        res = general.aggregate_and(data=[dp0,dp1,dp2], value_keys='a')
        result = ret(data=res)

        self.assertTrue(result, {'aggregate_and': False})




