from sly import Lexer, Parser
import operator
from enum import Enum
from ancile.web.errors import ParseError
from core.private_data import PrivateData


class RangeType(Enum):
    OPEN = 1     # (a,b)
    CLOSED = 2   # [a,b]
    LOPEN = 3    # (a,b]
    ROPEN = 4    # [a,b)


class ParamCell(object):
    """
    A simple data object that stores information about a parameter's
    requirements in a policy. Primary use is the evaluate method which checks a
    given input value for the parameter.
    """
    def __init__(self, name: str, operation, value):
        self.name = name
        self.op = operation
        self.value = value

    def evaluate(self, name_val) -> bool:
        """Evaluate the given value against the cell.

        returns name_val op value
        """
        return self.op(name_val, self.value)

    def __repr__(self):
        val_str = str(self.value) if not isinstance(self.value, str) \
                                  else f'"{self.value}"'
        return f'<ParamCell: {self.name} {self.op} {val_str}>'

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, ParamCell):
            return False
        else:
            return self.name == other.name and                                \
                   self.op == other.op and                                    \
                   self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)


class RangeCell(object):
    """
    A data object representing a parameter's requirements in a policy.
    Specifically for parameters that are limited to (or excluded from) a given 
    range.
    """

    def __init__(self, name: str, lower, upper, rtype: RangeType, invert_flag):
        self.name = name
        self.lower = lower
        self.upper = upper
        self.type = rtype
        self.invert_flag = invert_flag

    def evaluate(self, name_val) -> bool:
        if self.invert_flag:
            return not self._evaluate(name_val)
        else:
            return self._evaluate(name_val)

    def _evaluate(self, name_val) -> bool:
        if self.type == RangeType.OPEN:
            return self.lower < name_val < self.upper
        elif self.type == RangeType.CLOSED:
            return self.lower <= name_val <= self.upper
        elif self.type == RangeType.LOPEN:
            return self.lower < name_val <= self.upper
        else:
            return self.lower <= name_val < self.upper

    def __repr__(self):
        invert_str = '!' if self.invert_flag else ''
        if self.type == RangeType.OPEN:
            return f'<RangeCell: {invert_str} {self.lower} < {self.name} < {self.upper} >'
        elif self.type == RangeType.CLOSED:
            return f'<RangeCell: {invert_str} {self.lower} <= {self.name} <= {self.upper} >'
        elif self.type == RangeType.LOPEN:
            return f'<RangeCell: {invert_str} {self.lower} < {self.name} <= {self.upper} >'
        elif self.type == RangeType.ROPEN:
            return f'<RangeCell: {invert_str} {self.lower} <= {self.name} < {self.upper} >'

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, RangeCell):
            return False
        else:
            return self.name == other.name and                                \
                   self.lower == other.lower and                              \
                   self.upper == other.upper and                              \
                   self.type == other.type and                                \
                   self.invert_flag == other.invert_flag

    def __ne__(self, other):
        return not self.__eq__(other)

class SetCell(object):
    def __init__(self, name, in_objects, invert):
        self._set = set(in_objects)
        self._name = name
        self._invert_flag = invert

    def evaluate(self, name_val) -> bool:
        """Evaluate the given value against the cell.

        returns name_val op value
        """
        if not self._invert_flag:
            return name_val in self._set
        else:
            return name_val not in self._set

    def __repr__(self):
        inv_str = ' ' if not self._invert_flag else ' not '
        return f'<? SetCell: {self._name}{inv_str}in {self._set} ?>'

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, SetCell):
            return False
        else:
            return self._name == other._name and                              \
                   self._invert_flag == other._invert_flag and                \
                   self._set == other._set

    def __ne__(self, other):
        return not self.__eq__(other)


class PolicyLexer(Lexer):
    tokens = { TEXT, NUMBER, FLOAT, UNION, CONCAT, INTERSECT,  NEG, STAR,
               ANYF, LPAREN, RPAREN, LBRACKET, RBRACKET, COMMA, EQ,
               PRIVATE, STRING, NEQ, LEQ, LE, GEQ, GE, LBRACE, RBRACE, IN,
               TRUE, FALSE }
    ignore = ' \t\n\r\f\v'


    # Tokens
    TEXT = r'[a-zA-Z_][a-zA-Z0-9_]*'

    @_(r'[-\+]?\d+\.\d+')
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'[-\+]?\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'\"[a-zA-Z0-9_:/\. \t\'\@]*\"',
       r'\'[a-zA-Z0-9_:/\. \t\"\@]*\'')
    def STRING(self, t):
        if t.value.startswith('\''):
            t.value = t.value.strip("'")
        else:
            t.value = t.value.strip('"')
        return t

    TEXT['ANYF'] = ANYF
    TEXT['private'] = PRIVATE
    TEXT['in'] = IN
    TEXT['true'] = TEXT['True'] = TEXT['TRUE'] = TRUE
    TEXT['false'] = TEXT['False'] = TEXT['FALSE'] = FALSE


    # Special symbols

    UNION = r'\+'
    CONCAT = r'\.'
    INTERSECT = r'\&'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    LBRACE = r'\{'
    RBRACE = r'\}'
    # QUOTE = r'\"'
    COMMA = r'\,'
    NEQ = r'\!\='
    LEQ = r'\<\='
    LE = r'\<'
    GEQ = r'\>\='
    GE = r'\>'
    EQ = r'\='
    NEG = r'\!'
    STAR = r'\*'

    # Ignored pattern
    ignore_newline = r'\n+'

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

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
        return [p.policy_op, p.policy, p.rclause]

    @_('policy policy_op rclause')
    def rclause(self, p):
        return [p.policy_op, p.policy, p.rclause]

    @_('policy')
    def rclause(self, p):
        return p.policy

    @_('LPAREN clause RPAREN')
    def policy(self, p):
        return p.clause

    @_('INTERSECT')
    def policy_op(self, p):
        return 'intersect'

    @_('UNION')
    def policy_op(self, p):
        return 'union'

    @_('NEG policy')
    def policy(self, p):
        return ['neg', p.policy]

    @_('policy STAR')
    def policy(self, p):
        return ['star', p.policy]

    @_('policy')
    def clause(self, p):
        return p.policy

    @_('policy CONCAT policy')
    def policy(self, p):
        return ['concat', p.policy0, p.policy1]

    @_('NUMBER')
    def policy(self, p):
        return int(p.NUMBER)

    @_('TEXT')
    def policy(self, p):
        return ['exec', p.TEXT, {}]

    @_('ANYF')
    def policy(self, p):
        return ['exec', "ANYF"]

    @_('TEXT LPAREN params RPAREN')
    def policy(self, p):
        return ['exec', p.TEXT, p.params]

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