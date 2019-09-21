import unittest

from ancile.core.primitives.policy_helpers.expressions import *
from ancile.utils.errors import ParseError
from ancile.core.primitives import DataPolicyPair, Policy
from ancile.core.primitives import *

import logging

from test.unit.restricted.tools import display, ret

logger = logging.getLogger(__name__)

class ParserTests(unittest.TestCase):


    def test_simple(self):
        policy = 'test.ret'

        parsed_policy = Policy(policy)
        self.assertTrue(ConcatExpression(ActionExpression('test'), ActionExpression('ret')) ==
                        parsed_policy._policy_expr)


    def test_parsing_commands(self):
        policies = ['a+1', 'a.b', 'a&b', '!a', '!b.c', '0', '1']
        for x in policies:
            parsed_policy = Policy(x)
            self.assertTrue(parsed_policy.__repr__(), x)

