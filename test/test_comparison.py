import unittest
from test.tools import run_test
from src.micro_data_core_python.errors import ParseError


class ComparisonTests(unittest.TestCase):
    def test_simple(self):
        policy = ('edit.field_comparison(field_path="a", comparison_operator="eq", value=4)'
                  '.((_enforce_comparison(result=True).ret) + '
                  '(_enforce_comparison(result=False).test.ret))'
                 )
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4)\n"
                   "ret(data=dp0)\n"
                  )
        self.assertTrue(run_test(program, policy))

    def test_simple2(self):
        policy = ('edit.field_comparison(field_path="a", comparison_operator="eq", value=4)'
                  '.((_enforce_comparison(result=True).ret) + '
                  '(_enforce_comparison(result=False).test.ret))'
                 )
        program = ("edit(data=dp0, key='a', value=3)\n"
                   "general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4)\n"
                   "ret(data=dp0)\n"
                  )
        self.assertFalse(run_test(program, policy))

    def test_simple3(self):
        policy = ('edit.field_comparison(field_path="a", comparison_operator="eq", value=4)'
                  '.((_enforce_comparison(result=True).ret) + '
                  '(_enforce_comparison(result=False).test.ret))'
                 )
        program = ("edit(data=dp0, key='a', value=3)\n"
                   "if general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4):\n"
                   "    ret(data=dp0)\n"
                   "else:\n"
                   "    test(data=dp0);ret(data=dp0)\n"
                  )
        self.assertTrue(run_test(program, policy))

    def test_simple4(self):
        policy = ('edit.field_comparison(field_path="a", comparison_operator="eq", value=4)'
                  '.((_enforce_comparison(result=True).ret) + '
                  '(_enforce_comparison(result=False).test.ret))'
                 )
        program = ("edit(data=dp0, key='a', value=4)\n"
                   "if general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4):\n"
                   "    ret(data=dp0)\n"
                   "else:\n"
                   "    test(data=dp0);ret(data=dp0)\n"
                  )
        self.assertTrue(run_test(program, policy))

    def test_dependent1(self):
        policy0 = ('edit.field_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="1", name="1")'
                   '.((_enforce_comparison(result=True).ret) + '
                   '(_enforce_comparison(result=False).test.ret))'
                  )
        policy1 = ('edit.dependent_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="0", name="0")'
                  )
        program = ("edit(data=dp0, key='b', value=3)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "if general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4, dependent_dp=dp1):\n"
                   "    ret(data=dp0)\n"
                   "else:\n"
                   "    test(data=dp0);ret(data=dp0)\n"
                  )
        self.assertTrue(run_test(program, policy0, policy1))

    def test_dependent2(self):
        policy0 = ('edit.field_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="1", name="1")'
                   '.((_enforce_comparison(result=True).ret) + '
                   '(_enforce_comparison(result=False).test.ret))'
                  )
        policy1 = ('edit.dependent_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="0", name="0")'
                  )
        program = ("edit(data=dp0, key='b', value=3)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "if general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4, dependent_dp=dp1):\n"
                   "    ret(data=dp0)\n"
                   "else:\n"
                   "    test(data=dp0);ret(data=dp0)\n"
                   "ret(data=dp1)"
                  )
        self.assertFalse(run_test(program, policy0, policy1))

    def test_dependent3(self):
        policy0 = ('edit.field_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="1", name="1")'
                   '.((_enforce_comparison(result=True).ret) + '
                   '(_enforce_comparison(result=False).test.ret))'
                  )
        policy1 = ('edit.dependent_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="0", name="0")'
                   '.ret'
                  )
        program = ("edit(data=dp0, key='b', value=3)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "if general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4, dependent_dp=dp1):\n"
                   "    ret(data=dp0)\n"
                   "else:\n"
                   "    test(data=dp0);ret(data=dp0)\n"
                   "ret(data=dp1)"
                  )
        self.assertTrue(run_test(program, policy0, policy1))

    def test_dependent4(self):
        policy0 = ('edit.field_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="1", name="1")'
                   '.((_enforce_comparison(result=True).ret) + '
                   '(_enforce_comparison(result=False).test.ret))'
                  )
        policy1 = ('edit.dependent_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="0", name="0")'
                  )
        program = ("edit(data=dp0, key='b', value=3)\n"
                   "edit(data=dp1, key='a', value=3)\n"
                   "general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4, dependent_dp=dp1)\n"
                   "ret(data=dp0)\n"
                  )
        self.assertFalse(run_test(program, policy0, policy1))

    def test_dependent5(self):
        policy0 = ('edit.field_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="1", name="1")'
                   '.((_enforce_comparison(result=True).ret) + '
                   '(_enforce_comparison(result=False).test.ret))'
                  )
        policy1 = ('edit.dependent_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="0", name="0")'
                  )
        program = ("edit(data=dp0, key='b', value=3)\n"
                   "edit(data=dp1, key='a', value=4)\n"
                   "general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4, dependent_dp=dp1)\n"
                   "ret(data=dp0)\n"
                  )
        self.assertTrue(run_test(program, policy0, policy1))

    def test_dependent6(self):
        policy0 = ('edit.field_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="1", name="1")'
                   '.((_enforce_comparison(result=True).ret) + '
                   '(_enforce_comparison(result=False).test.ret))'
                  )
        policy1 = ('edit.dependent_comparison(field_path="a", '
                   'comparison_operator="eq", value=4, username="0", name="0")'
                  )
        program = ("edit(data=dp0, key='b', value=3)\n"
                   "edit(data=dp1, key='a', value=3)\n"
                   "general.field_comparison(data=dp0, field_path='a', comparison_operator='eq',"
                   " value=4, dependent_dp=dp1)\n"
                   "test(data=dp0);ret(data=dp0)\n"
                  )
        self.assertTrue(run_test(program, policy0, policy1))
