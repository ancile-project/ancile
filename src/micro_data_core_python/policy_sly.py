from sly import Lexer, Parser
from src.micro_data_core_python.datapolicypair import PrivateData
import operator
from enum import Enum
from src.micro_data_core_python.errors import ParseError


class RangeType(Enum):
    OPEN = 1     # (a,b)
    CLOSED = 2   # [a,b]
    LOPEN = 3    # (a,b]
    ROPEN = 4    # [a,b)


class ParamCell(object):
    def __init__(self, name: str, operation, value):
        self.name = name
        self.op = operation
        self.value = value

    def evaluate(self, name_val) -> bool:
        """Evaluate the given value against the cell.

        returns name op value
        """
        return self.op(name_val, self.value)

    def __repr__(self):
        return f'<ParamCell: {self.name} {self.op} {self.value}>'


class RangeCell(ParamCell):
    def __init__(self, name, lower, upper, rtype: RangeType):
        self.name = name
        self.lower = lower
        self.upper = upper
        self.type = rtype

    def evaluate(self, name_val) -> bool:
        if self.type == RangeType.OPEN:
            return self.lower < name_val < self.upper
        elif self.type == RangeType.CLOSED:
            return self.lower <= name_val <= self.upper
        elif self.type == RangeType.LOPEN:
            return self.lower < name_val <= self.upper
        else:
            return self.lower <= name_val < self.upper

    def __repr__(self):
        if self.type == RangeType.OPEN:
            return f'<RangeCell: {self.lower} < {self.name} < {self.upper} >'
        elif self.type == RangeType.CLOSED:
            return f'<RangeCell: {self.lower} <= {self.name} <= {self.upper} >'
        elif self.type == RangeType.LOPEN:
            return f'<RangeCell: {self.lower} < {self.name} <= {self.upper} >'
        elif self.type == RangeType.ROPEN:
            return f'<RangeCell: {self.lower} <= {self.name} < {self.upper} >'



class PolicyLexer(Lexer):
    tokens = { TEXT, NUMBER, FLOAT, UNION, CONCAT, INTERSECT,  NEG, STAR,
               ANYF, LPAREN, RPAREN, LBRACKET, RBRACKET, COMMA, EQ,
               PRIVATE, STRING, NEQ, LEQ, LE, GEQ, GE }
    ignore = ' \s\t\n\r'


    ANYF = 'ANYF'
    PRIVATE = 'private'
    # Tokens
    TEXT = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\"[a-zA-Z_][a-zA-Z0-9_:/\.]*\"'
    FLOAT = r'[-\+]?\d+\.\d+'
    NUMBER = r'[-\+]?\d+'


    # Special symbols

    UNION = r'\+'
    CONCAT = r'\.'
    INTERSECT = r'\&'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    # LBRACE = r'\{'
    # RBRACE = r'\}'
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

    # comparison operators
    # COMPARISON = r'(\<\=)|(\>\=)|(\<)|(\>)|(\!\=)'

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

    precedence = (
        ('right', CONCAT, UNION, INTERSECT),
        ('left', STAR, NEG),
        )

    def __init__(self):
        self.names = { }

    @_('NUMBER')
    def clause(self, p):
        return int(p.NUMBER)

    @_('TEXT')
    def clause(self, p):
        return ['exec', p.TEXT, []]

    @_('ANYF')
    def clause(self, p):
        return ['exec', "ANYF"]

    @_('clause CONCAT clause')
    def clause(self, p):
        return ['concat', p.clause0, p.clause1]

    @_('clause UNION clause')
    def clause(self, p):
        return ['union', p.clause0, p.clause1]

    @_('LPAREN clause RPAREN')
    def clause(self, p):
        return p.clause

    @_('clause INTERSECT clause')
    def clause(self, p):
        return ['intersect', p.clause0, p.clause1]

    @_('NEG clause')
    def clause(self, p):
        return ['NEG', p.clause]

    @_('clause STAR')
    def clause(self, p):
        return ['star', p.clause]

    @_('TEXT LPAREN params RPAREN')
    def clause(self, p):
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
        return {p.TEXT: ParamCell(p.TEXT, p.equality_op, p.STRING.strip('"'))}

    @_('TEXT numeric_op NUMBER')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, p.numeric_op, int(p.NUMBER))}

    @_('TEXT numeric_op FLOAT')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, p.numeric_op, float(p.FLOAT))}

    @_('TEXT equality_op LBRACKET plists RBRACKET')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, operator.eq, p.plists)}

    @_('TEXT EQ PRIVATE LPAREN STRING RPAREN')
    def param(self, p):
        return {p.TEXT: ParamCell(p.TEXT, operator.eq,
                                  PrivateData(p.STRING.strip('"')))}

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

        return {p.TEXT: RangeCell(p.TEXT, lower, upper, type_val)}

    @_('NUMBER')
    def numeric(self, p):
        return int(p.NUMBER)

    @_('FLOAT')
    def numeric(self, p):
        return float(p.NUMBER)

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



    # @_('TEXT EQ comparison')
    # def param(self, p):
    #     return {p.TEXT: p.comparison}

    @_('TEXT EQ TEXT')
    def param(self, p):
        value = None
        if p.TEXT1.lower() == 'false':
            value = False
        elif p.TEXT1.lower() == 'true':
            value = True
        return {p.TEXT0: value}

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
        return [p.STRING.strip('"')]

    @_('FLOAT')
    def plist(self, p):
        return [float(p.FLOAT)]

    @_('NUMBER')
    def plist(self, p):
        return [int(p.NUMBER)]

    # @_('EQ')
    # def comparison(self, p):
    #     return operator.eq
    
    # @_('COMPARISON')
    # def comparison(self, p):
    #     if p.COMPARISON == '<=': return operator.le
    #     elif p.COMPARISON == '<': return operator.lt
    #     elif p.COMPARISON == '>=': return operator.ge
    #     elif p.COMPARISON == '>': return operator.gt

    # @_('NEG EQ')
    # def comparison(self, p):
    #     return operator.ne

    @staticmethod
    def parse_it(text):
        lexer = PolicyLexer()
        parser = PolicyParser()
        return parser.parse(lexer.tokenize(text))

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