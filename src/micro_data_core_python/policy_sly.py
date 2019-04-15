from sly import Lexer, Parser

class PolicyLexer(Lexer):
    tokens = { TEXT, NUMBER, FLOAT, UNION, CONCAT, INTERSECT,  NEG, STAR,
               ANYF, LPAREN, RPAREN, LBRACKET, RBRACKET, QUOTE, COMMA, EQ }
    ignore = ' \s\t\n\r'

    # Tokens
    TEXT = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUMBER = r'\d+'
    FLOAT = r'\f+'

    # Special symbols
    UNION = r'\+'
    CONCAT = r'\.'
    INTERSECT = r'\&'
    ANYF = 'ANYF'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    QUOTE = r'\"'
    COMMA = r'\,'
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

    @_('TEXT EQ QUOTE TEXT QUOTE')
    def param(self, p):
        return {p.TEXT0: p.TEXT1}

    @_('TEXT EQ NUMBER')
    def param(self, p):
        return {p.TEXT: int(p.NUMBER)}

    @_('TEXT EQ FLOAT')
    def param(self, p):
        return {p.TEXT: float(p.FLOAT)}

    @_('TEXT EQ LBRACKET plists RBRACKET')
    def param(self, p):

        return {p.TEXT: p.plists}

    @_('plist')
    def plists(self, p):
        return p.plist

    @_('plist COMMA plists')
    def plists(self, p):
        params = p.plist
        params.extend(p.plists)
        return params

    @_('QUOTE TEXT QUOTE')
    def plist(self, p):
        return [p.TEXT]

    @_('FLOAT')
    def plist(self, p):
        return [float(p.FLOAT)]

    @_('NUMBER')
    def plist(self, p):
        return [int(p.NUMBER)]

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
            print(parser.parse(lexer.tokenize(text)))