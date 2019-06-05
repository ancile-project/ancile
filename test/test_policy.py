import unittest
from test.tools import run_test
from src.micro_data_core_python.errors import ParseError


class FunctionTests(unittest.TestCase):
    def test_simple(self):
        policy = 'test.ret'
        program = "test(data=dp);ret(data=dp)"
        self.assertTrue(run_test(policy, program))

    def test_simple_two(self):
        policy = 'test.filter.view.ret'
        program = "test(data=dp);filter(data=dp);view(data=dp);ret(data=dp)"
        self.assertTrue(run_test(policy, program))

    def test_simple_error(self):
        policy = 'test.ret'
        program = "ret(data=dp)"
        self.assertFalse(run_test(policy, program))

    def test_simple_error_two(self):
        policy = 'test.test.ret'
        program = "test(data=dp);ret(data=dp)"
        self.assertFalse(run_test(policy, program))


class ParamEqualityTests(unittest.TestCase):
    def test_no_policy_params(self):
        policy = 'test'
        program = "test(data=dp, a=4, b=5)"
        self.assertTrue(run_test(policy, program))

    def test_simple_params(self):
        policy = 'test(a=4)'
        program = "test(data=dp, a=4, b=5)"
        self.assertTrue(run_test(policy, program))

    def test_simple_params_two(self):
        policy = 'test(a=4, b=5.0)'
        program = "test(data=dp, a=4, b=5)"
        self.assertTrue(run_test(policy, program))

    def test_simple_params_three(self):
        policy = 'test(a=4, b=5.0)'
        program = "test(data=dp, a=4, b=\"q\")"
        self.assertFalse(run_test(policy, program))

    def test_not_eq(self):
        policy = 'test(a!=4, b=5.0)'
        program = "test(data=dp, a=4, b=5)"
        self.assertFalse(run_test(policy, program))

    def test_not_eq_two(self):
        policy = 'test(a!=4, b=5.0)'
        program = "test(data=dp, a=6, b=5)"
        self.assertTrue(run_test(policy, program))

    def test_int_eq(self):
        policy = 'test(a=147, b=-5)'
        program = "test(data=dp, a=147, b=-5)"
        self.assertTrue(run_test(policy, program))

    def test_int_neq(self):
        policy = 'test(a!=147, b!=-5)'
        program = "test(data=dp, a=148, b=5)"
        self.assertTrue(run_test(policy, program))

    def test_float_eq(self):
        policy = 'test(a=0.45, b=-5.0)'
        program = "test(data=dp, a=0.45, b=-5.0)"
        self.assertTrue(run_test(policy, program))

    def test_float_neq(self):
        policy = 'test(a!=0.45, b!=-5.0)'
        program = "test(data=dp, a=0.46, b=-0.02)"
        self.assertTrue(run_test(policy, program))

    def test_string_eq(self):
        policy = 'test(a="string", b="strong")'
        program = "test(data=dp, a='string', b='strong')"
        self.assertTrue(run_test(policy, program))

    def test_string_neq(self):
        policy = 'test(a!="string", b!="strong")'
        program = "test(data=dp, a='stringy', b='strongy')"
        self.assertTrue(run_test(policy, program))

    def test_string_neq_2(self):
        policy = 'test(a!="string", b!="strong")'
        program = "test(data=dp, a='string', b='strong')"
        self.assertFalse(run_test(policy, program))

    def test_list_eq(self):
        policy = 'test(a=[1,2,3], b=["strong"])'
        program = "test(data=dp, a=[1,2,3], b=['strong'])"
        self.assertTrue(run_test(policy, program))

    def test_list_eq2(self):
        policy = 'test(a=[1,2,3], b=["strong"])'
        program = "test(data=dp, a=[1,2,3,4], b=['strong'])"
        self.assertFalse(run_test(policy, program))

    def test_list_neq(self):
        policy = 'test(a=[1,2,3], b!=["strong"])'
        program = "test(data=dp, a=[1,2,3], b=['weak'])"
        self.assertTrue(run_test(policy, program))

    def test_list_neq_2(self):
        policy = 'test(a!=[1,2,3], b=["strong"])'
        program = "test(data=dp, a=[1,2,3], b=['strong'])"
        self.assertFalse(run_test(policy, program))

    def test_list_exception(self):
        policy = 'test(a!=[1,2,3], b>["strong"])'
        program = "test(data=dp, a=[1,2,3], b=['strong'])"
        with self.assertRaises(ParseError):
            run_test(policy, program)

    def test_string_exception(self):
        policy = 'test(a!=[1,2,3], b> "strong")'
        program = "test(data=dp, a=[1,2,3], b='strong')"
        with self.assertRaises(ParseError):
            run_test(policy, program)


class ParamInequalityTest(unittest.TestCase):
    def test_inequality(self):
        policy = 'test(a < 5, b > 0)'
        program = "test(data=dp, a=6, b=-1)"
        self.assertFalse(run_test(policy, program))

    def test_inequality_2(self):
        policy = 'test(a < 5, b > 0)'
        program = "test(data=dp, a=4, b=2)"
        self.assertTrue(run_test(policy, program))

    def test_inequality_3(self):
        policy = 'test(a <= 5, b >= 0)'
        program = "test(data=dp, a=5, b=0)"
        self.assertTrue(run_test(policy, program))

    def test_inequality_4(self):
        policy = 'test(a <= 5.0, b >= -0.8)'
        program = "test(data=dp, a=5.0, b=0)"
        self.assertTrue(run_test(policy, program))

    def test_inequality_5(self):
        policy = 'test(a < 5.0, b >= -0.8)'
        program = "test(data=dp, a=4.99, b=0)"
        self.assertTrue(run_test(policy, program))

    def test_inequality_6(self):
        policy = 'test(a > 5.8, b >= -0.8)'
        program = "test(data=dp, a=4.99, b=0)"
        self.assertFalse(run_test(policy, program))


class ParamRangeTests(unittest.TestCase):
    def test_range1(self):
        policy = 'test(4 < a < 5.0, -0.8 <= b < 4.6)'
        program = "test(data=dp, a=4.99, b=0)"
        self.assertTrue(run_test(policy, program))

    def test_range2(self):
        policy = 'test(4 < a < 5.0, -0.8 <= b < 4.6)'
        program = "test(data=dp, a=5, b=0)"
        self.assertFalse(run_test(policy, program))

    def test_range3(self):
        policy = 'test(4 < a < 5.0, -0.8 <= b < 4.6)'
        program = "test(data=dp, a=4.1, b=-0.8)"
        self.assertTrue(run_test(policy, program))

    def test_range4(self):
        policy = 'test(4 < a < 5.0, -0.8 <= b < 4.6)'
        program = "test(data=dp, a=4, b=0)"
        self.assertFalse(run_test(policy, program))

    def test_range5(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=4, b=0)"
        self.assertTrue(run_test(policy, program))

    def test_range6(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=4.9, b=0)"
        self.assertTrue(run_test(policy, program))

    def test_range7(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=5, b=0)"
        self.assertFalse(run_test(policy, program))

    def test_range8(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=4, b=4.6)"
        self.assertTrue(run_test(policy, program))

    def test_range9(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=4, b=-17)"
        self.assertFalse(run_test(policy, program))

    def test_range10(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=5, b=0)"
        self.assertFalse(run_test(policy, program))

    def test_range11(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=3.9, b=-16.9)"
        self.assertFalse(run_test(policy, program))

    def test_range12(self):
        policy = 'test(! 4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=3.9, b=-16.9)"
        self.assertTrue(run_test(policy, program))

    def test_range13(self):
        policy = 'test(! 4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp, a=4, b=-16.9)"
        self.assertFalse(run_test(policy, program))

    def test_range14(self):
        policy = 'test(4 <= a < 5, !-17 < b <= 4.6)'
        program = "test(data=dp, a=4, b=-16.9)"
        self.assertFalse(run_test(policy, program))