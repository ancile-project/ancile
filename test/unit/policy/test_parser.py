import unittest
from ancile.utils.errors import ParseError
from ancile.core.primitives import DataPolicyPair, Policy

import logging
logger = logging.getLogger(__name__)

class ParserTests(unittest.TestCase):


    def test_simple(self):
        policy = 'test.ret'

        parsed_policy = Policy(policy)
        self.assertTrue(['concat', ['exec', 'test', {}], ['exec', 'ret', {}]] == parsed_policy._policy)


    def test_simple_raise(self):
        policy = 'test.^ret'
        print(policy)
        parsed_policy = Policy(policy)
        print(parsed_policy)


    def test_complex_param(self):
        policy = 'test(a>4)'
        print(policy)
        parsed_policy = Policy(policy)
        print(parsed_policy)
