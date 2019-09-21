from sly import Parser
import operator

from ancile.core.primitives.policy_helpers.expressions.special.assignment_expression import AssignmentExpression
from ancile.utils.errors import ParseError
from ancile.core.primitives.policy_helpers.private_data import PrivateData
from ancile.core.primitives.policy_helpers.policy_lexer import *
from ancile.core.primitives.policy_helpers.params import ParamCell, RangeCell, SetCell, RangeType
from ancile.core.primitives.policy_helpers.expressions import *


class PolicyParser(Parser):
    tokens = PolicyLexer.tokens

    start = 'clause'

    precedence = (
        ('right', CONCAT, UNION, INTERSECT),
        ('left', STAR, NEG),
        )

    def __init__(self):
        self.names = { }

    def error(self, token):
        raise ParseError(f'Error at token {token}')


    @_('policy policy_op rclause')
    def clause(self, p):
        return p.policy_op(p.policy, p.rclause)

    @_('policy policy_op rclause')
    def rclause(self, p):
        return p.policy_op(p.policy, p.rclause)

    @_('policy')
    def rclause(self, p):
        return p.policy

    @_('LPAREN clause RPAREN')
    def policy(self, p):
        return p.clause

    @_('INTERSECT')
    def policy_op(self, p):
        return IntersectExpression

    @_('UNION')
    def policy_op(self, p):
        return UnionExpression

    @_('NEG policy')
    def policy(self, p):
        return NegationExpression(p.policy)

    @_('policy STAR')
    def policy(self, p):
        return StarExpression(p.policy)

    @_('TEST test_expr')
    def policy(self, p):
        return ConstantExpression(Constants.ONE)
    #
    # @_('testvar UNION test_expr')
    # def test_expr(self, p):
    #     return UnionExpression(p.testvar, p.test_expr)

    @_('testvar')
    def test_expr(self, p):
        return p.testvar

    @_('TESTVAR')
    def testvar(self, p):
        return AssignmentExpression(p.TESTVAR, Constants.ONE)

    @_('policy')
    def clause(self, p):
        return p.policy

    @_('policy CONCAT policy')
    def policy(self, p):
        return ConcatExpression(p.policy0, p.policy1)

    @_('NUMBER')
    def policy(self, p):
        val = int(p.NUMBER)
        if val == 0:
            return ConstantExpression(Constants.ZERO)
        elif val == 1:
            return ConstantExpression(Constants.ONE)
        else:
            raise ParseError(f'Provided invalid value: {val}')

    @_('TEXT')
    def policy(self, p):
        return ActionExpression(p.TEXT)

    @_('ANYF')
    def policy(self, p):
        return ActionExpression("ANYF")

    @_('TEXT LPAREN params RPAREN')
    def policy(self, p):
        return ActionExpression(p.TEXT, p.params)

    @_('param COMMA params')
    def params(self, p):
        params = p.param
        params.update(p.params)
        return params

    @_('param')
    def params(self, p):
        return p.param

    @_('TEXT equality_op STRING')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, p.equality_op, p.STRING)}

    @_('TEXT numeric_op NUMBER')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, p.numeric_op, int(p.NUMBER))}

    @_('TEXT numeric_op FLOAT')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, p.numeric_op, float(p.FLOAT))}

    @_('TEXT equality_op LBRACKET plists RBRACKET')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, p.equality_op, p.plists)}

    @_('TEXT EQ PRIVATE LPAREN STRING RPAREN')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, operator.eq,
                                  PrivateData(p.STRING))}

    @_('numeric range_op TEXT range_op numeric')
    def param(self, p):
        lower = p.numeric0
        upper = p.numeric1
        comp1 = p.range_op0
        comp2 = p.range_op1

        if comp1 == operator.lt and comp2 == operator.lt:
            type_val = RangeType.OPEN
        elif comp1 == operator.le and comp2 == operator.le:
            type_val = RangeType.CLOSED
        elif comp1 == operator.lt and comp2 == operator.le:
            type_val = RangeType.LOPEN
        elif comp1 == operator.le and comp2 == operator.lt:
            type_val = RangeType.ROPEN
        else:
            raise ParseError("Invalid range")

        return {p.TEXT: RangeCell(p.TEXT, lower, upper, type_val, False)}

    @_('NEG numeric range_op TEXT range_op numeric')
    def param(self, p):
        lower = p.numeric0
        upper = p.numeric1
        comp1 = p.range_op0
        comp2 = p.range_op1

        if comp1 == operator.lt and comp2 == operator.lt:
            type_val = RangeType.OPEN
        elif comp1 == operator.le and comp2 == operator.le:
            type_val = RangeType.CLOSED
        elif comp1 == operator.lt and comp2 == operator.le:
            type_val = RangeType.LOPEN
        elif comp1 == operator.le and comp2 == operator.lt:
            type_val = RangeType.ROPEN
        else:
            raise ParseError("Invalid range")

        return {p.TEXT: RangeCell(p.TEXT, lower, upper, type_val, True)}

    @_('TEXT IN LBRACE sets RBRACE')
    def param(self, p):
        return {p.TEXT: SetCell(p.TEXT, p.sets, False)}

    @_('NEG TEXT IN LBRACE sets RBRACE')
    def param(self, p):
        return {p.TEXT: SetCell(p.TEXT, p.sets, True)}

    @_('set_elem COMMA sets')
    def sets(self, p):
        element = [p.set_elem]
        elements = element + p.sets
        return elements

    @_('set_elem')
    def sets(self, p):
        return [p.set_elem]

    @_('numeric')
    def set_elem(self, p):
        return p.numeric

    @_('STRING')
    def set_elem(self, p):
        return p.STRING

    @_('NUMBER')
    def numeric(self, p):
        return p.NUMBER

    @_('FLOAT')
    def numeric(self, p):
        return p.FLOAT

    @_('equality_op')
    def numeric_op(self, p):
        return p.equality_op

    @_('comparison_op')
    def numeric_op(self, p):
        return p.comparison_op

    @_('EQ')
    def equality_op(self, p):
        return operator.eq

    @_('NEQ')
    def equality_op(self, p):
        return operator.ne

    @_('LEQ')
    def comparison_op(self, p):
        return operator.le

    @_('LE')
    def comparison_op(self, p):
        return operator.lt

    @_('GEQ')
    def comparison_op(self, p):
        return operator.ge

    @_('GE')
    def comparison_op(self, p):
        return operator.gt

    @_('LEQ')
    def range_op(self, p):
        return operator.le

    @_('LE')
    def range_op(self, p):
        return operator.lt

    @_('TEXT EQ bool_val')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, operator.eq, p.bool_val)}

    @_('FALSE')
    def bool_val(self, p):
        return False

    @_('TRUE')
    def bool_val(self, p):
        return True

    @_('plist')
    def plists(self, p):
        return p.plist

    @_('plist COMMA plists')
    def plists(self, p):
        params = p.plist
        params.extend(p.plists)
        return params

    @_('STRING')
    def plist(self, p):
        return [p.STRING]

    @_('FLOAT')
    def plist(self, p):
        return [p.FLOAT]

    @_('NUMBER')
    def plist(self, p):
        return [p.NUMBER]

    @staticmethod
    def parse_it(text):
        lexer = PolicyLexer()
        parser = PolicyParser()
        parsed = parser.parse(lexer.tokenize(text))
        return parsed

    @staticmethod
    def parse_policies(policies):
        parsed_policies = dict()
        for provider, policy in policies.items():
            parsed_policies[provider] = PolicyParser.parse_it(policy)
        return parsed_policies


if __name__ == '__main__':
    lexer = PolicyLexer()
    parser = PolicyParser()
    while True:
        try:
            text = input('calc > ')
        except EOFError:
            break
        if text:
            lexed = lexer.tokenize(text)
            # print(f"lexed: {list(lexed)}\n")
            print(parser.parse(lexed))
