import unittest
from test.tools import run_test
from ancile_web.errors import ParseError


class FunctionTests(unittest.TestCase):
    def test_simple(self):
        policy = 'test.ret'
        program = "test(data=dp0);ret(data=dp0)"
        self.assertTrue(run_test(program, policy))

    def test_simple_two(self):
        policy = 'test.filter.view.ret'
        program = "test(data=dp0);filter(data=dp0);view(data=dp0);ret(data=dp0)"
        self.assertTrue(run_test(program, policy))

    def test_simple_error(self):
        policy = 'test.ret'
        program = "ret(data=dp0)"
        self.assertFalse(run_test(program, policy))

    def test_simple_error_two(self):
        policy = 'test.test.ret'
        program = "test(data=dp0);ret(data=dp0)"
        self.assertFalse(run_test(program, policy))

    def test_simple_error_three(self):
        policy = 'test'
        program = "test(data=dp0);ret(data=dp0)"
        self.assertFalse(run_test(program, policy))

    def test_simple_error_four(self):
        policy = 'test'
        program = "test(data=dp0);test(data=dp0);ret(data=dp0)"
        self.assertFalse(run_test(program, policy))

    def test_intersect_star_fail(self):
        policy = '1&test*'
        program = "test(data=dp0)"
        self.assertFalse(run_test(program, policy))

    def test_intersect_1_1_pass(self):
        policy = 'ret.(1&1)'
        program = "ret(data=dp0)"
        self.assertTrue(run_test(program, policy))

    def test_intersect_1_0_fail(self):
        policy = 'ret.(1&0)'
        program = "ret(data=dp0)"
        self.assertFalse(run_test(program, policy))

    def test_union_star(self):
        policy = '1+test*'
        program = "test(data=dp0)"
        self.assertTrue(run_test(program, policy))

class ParamEqualityTests(unittest.TestCase):

    def test_no_policy_params(self):
        policy = 'test'
        program = "test(data=dp0, a=4, b=5)"
        self.assertTrue(run_test(program, policy))

    def test_simple_params(self):
        policy = 'test(a=4)'
        program = "test(data=dp0, a=4, b=5)"
        self.assertTrue(run_test(program, policy))

    def test_simple_params_two(self):
        policy = 'test(a=4, b=5.0)'
        program = "test(data=dp0, a=4, b=5)"
        self.assertTrue(run_test(program, policy))

    def test_simple_params_three(self):
        policy = 'test(a=4, b=5.0)'
        program = "test(data=dp0, a=4, b=\"q\")"
        self.assertFalse(run_test(program, policy))

    def test_not_eq(self):
        policy = 'test(a!=4, b=5.0)'
        program = "test(data=dp0, a=4, b=5)"
        self.assertFalse(run_test(program, policy))

    def test_not_eq_two(self):
        policy = 'test(a!=4, b=5.0)'
        program = "test(data=dp0, a=6, b=5)"
        self.assertTrue(run_test(program, policy))

    def test_int_eq(self):
        policy = 'test(a=147, b=-5)'
        program = "test(data=dp0, a=147, b=-5)"
        self.assertTrue(run_test(program, policy))

    def test_int_neq(self):
        policy = 'test(a!=147, b!=-5)'
        program = "test(data=dp0, a=148, b=5)"
        self.assertTrue(run_test(program, policy))

    def test_float_eq(self):
        policy = 'test(a=0.45, b=-5.0)'
        program = "test(data=dp0, a=0.45, b=-5.0)"
        self.assertTrue(run_test(program, policy))

    def test_float_neq(self):
        policy = 'test(a!=0.45, b!=-5.0)'
        program = "test(data=dp0, a=0.46, b=-0.02)"
        self.assertTrue(run_test(program, policy))

    def test_string_eq(self):
        policy = 'test(a="string", b="strong")'
        program = "test(data=dp0, a='string', b='strong')"
        self.assertTrue(run_test(program, policy))

    def test_string_neq(self):
        policy = 'test(a!="string", b!="strong")'
        program = "test(data=dp0, a='stringy', b='strongy')"
        self.assertTrue(run_test(program, policy))

    def test_string_neq_2(self):
        policy = 'test(a!="string", b!="strong")'
        program = "test(data=dp0, a='string', b='strong')"
        self.assertFalse(run_test(program, policy))

    def test_list_eq(self):
        policy = 'test(a=[1,2,3], b=["strong"])'
        program = "test(data=dp0, a=[1,2,3], b=['strong'])"
        self.assertTrue(run_test(program, policy))

    def test_list_eq2(self):
        policy = 'test(a=[1,2,3], b=["strong"])'
        program = "test(data=dp0, a=[1,2,3,4], b=['strong'])"
        self.assertFalse(run_test(program, policy))

    def test_list_neq(self):
        policy = 'test(a=[1,2,3], b!=["strong"])'
        program = "test(data=dp0, a=[1,2,3], b=['weak'])"
        self.assertTrue(run_test(program, policy))

    def test_list_neq_2(self):
        policy = 'test(a!=[1,2,3], b=["strong"])'
        program = "test(data=dp0, a=[1,2,3], b=['strong'])"
        self.assertFalse(run_test(program, policy))

    def test_list_exception(self):
        policy = 'test(a!=[1,2,3], b>["strong"])'
        program = "test(data=dp0, a=[1,2,3], b=['strong'])"
        with self.assertRaises(ParseError):
            run_test(program, policy)

    def test_string_exception(self):
        policy = 'test(a!=[1,2,3], b> "strong")'
        program = "test(data=dp0, a=[1,2,3], b='strong')"
        with self.assertRaises(ParseError):
            run_test(program, policy)


class ParamInequalityTest(unittest.TestCase):
    def test_inequality(self):
        policy = 'test(a < 5, b > 0)'
        program = "test(data=dp0, a=6, b=-1)"
        self.assertFalse(run_test(program, policy))

    def test_inequality_2(self):
        policy = 'test(a < 5, b > 0)'
        program = "test(data=dp0, a=4, b=2)"
        self.assertTrue(run_test(program, policy))

    def test_inequality_3(self):
        policy = 'test(a <= 5, b >= 0)'
        program = "test(data=dp0, a=5, b=0)"
        self.assertTrue(run_test(program, policy))

    def test_inequality_4(self):
        policy = 'test(a <= 5.0, b >= -0.8)'
        program = "test(data=dp0, a=5.0, b=0)"
        self.assertTrue(run_test(program, policy))

    def test_inequality_5(self):
        policy = 'test(a < 5.0, b >= -0.8)'
        program = "test(data=dp0, a=4.99, b=0)"
        self.assertTrue(run_test(program, policy))

    def test_inequality_6(self):
        policy = 'test(a > 5.8, b >= -0.8)'
        program = "test(data=dp0, a=4.99, b=0)"
        self.assertFalse(run_test(program, policy))


class ParamRangeTests(unittest.TestCase):
    def test_range1(self):
        policy = 'test(4 < a < 5.0, -0.8 <= b < 4.6)'
        program = "test(data=dp0, a=4.99, b=0)"
        self.assertTrue(run_test(program, policy))

    def test_range2(self):
        policy = 'test(4 < a < 5.0, -0.8 <= b < 4.6)'
        program = "test(data=dp0, a=5, b=0)"
        self.assertFalse(run_test(program, policy))

    def test_range3(self):
        policy = 'test(4 < a < 5.0, -0.8 <= b < 4.6)'
        program = "test(data=dp0, a=4.1, b=-0.8)"
        self.assertTrue(run_test(program, policy))

    def test_range4(self):
        policy = 'test(4 < a < 5.0, -0.8 <= b < 4.6)'
        program = "test(data=dp0, a=4, b=0)"
        self.assertFalse(run_test(program, policy))

    def test_range5(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=4, b=0)"
        self.assertTrue(run_test(program, policy))

    def test_range6(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=4.9, b=0)"
        self.assertTrue(run_test(program, policy))

    def test_range7(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=5, b=0)"
        self.assertFalse(run_test(program, policy))

    def test_range8(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=4, b=4.6)"
        self.assertTrue(run_test(program, policy))

    def test_range9(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=4, b=-17)"
        self.assertFalse(run_test(program, policy))

    def test_range10(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=5, b=0)"
        self.assertFalse(run_test(program, policy))

    def test_range11(self):
        policy = 'test(4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=3.9, b=-16.9)"
        self.assertFalse(run_test(program, policy))

    def test_range12(self):
        policy = 'test(! 4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=3.9, b=-16.9)"
        self.assertTrue(run_test(program, policy))

    def test_range13(self):
        policy = 'test(! 4 <= a < 5, -17 < b <= 4.6)'
        program = "test(data=dp0, a=4, b=-16.9)"
        self.assertFalse(run_test(program, policy))

    def test_range14(self):
        policy = 'test(4 <= a < 5, !-17 < b <= 4.6)'
        program = "test(data=dp0, a=4, b=-16.9)"
        self.assertFalse(run_test(program, policy))

class ParamSetTests(unittest.TestCase):
    def test_set1(self):
        policy = 'test(a in {4, 5, 6}, b in {"a", "b", "C"})'
        program = "test(data=dp0, a=4, b='a')"
        self.assertTrue(run_test(program, policy))

    def test_set2(self):
        policy = 'test(a in {4, 5, 6}, b in {"a", "b", "C"})'
        program = "test(data=dp0, a=-3, b='a')"
        self.assertFalse(run_test(program, policy))

    def test_set3(self):
        policy = 'test(a in {4, 5, 6}, b in {"a", "b", "C"})'
        program = "test(data=dp0, a=5, b='b')"
        self.assertTrue(run_test(program, policy))

    def test_set4(self):
        policy = 'test(a in {4, 5, 6}, b in {"a", "b", "C"})'
        program = "test(data=dp0, a=6, b='C')"
        self.assertTrue(run_test(program, policy))

    def test_set5(self):
        policy = 'test(a in {4, 5, 6}, b in {"a", "b", "C"})'
        program = "test(data=dp0, a=4.0, b='a')"
        self.assertTrue(run_test(program, policy))

    def test_set6(self):
        policy = 'test(! a in {4, 5, 6}, b in {"a", "b", "C"})'
        program = "test(data=dp0, a=3, b='a')"
        self.assertTrue(run_test(program, policy))

    def test_set7(self):
        policy = 'test(a in {4, 5.0, 6}, ! b in {"a", "b", "C"})'
        program = "test(data=dp0, a=5, b='a')"
        self.assertFalse(run_test(program, policy))