from sly import Lexer, Parser

class PolicyLexer(Lexer):
    tokens = { TEXT, NUMBER, UNION, CONCAT, INTERSECT,  NEG, STAR, ANYF }
    ignore = ' \s\t\n\r'

    # Tokens
    TEXT = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUMBER = r'\d+'

    # Special symbols
    UNION = r'\+'
    CONCAT = r'\.'
    INTERSECT = r'\&'
    ANYF = 'ANYF'
    # LPAREN = r'\('
    # RPAREN = r'\)'
    # LBRACKET = r'\['
    # RBRACKET = r'\]'
    # LPAREN, RPAREN, LBRACKET, RBRACKET,
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
        return ['exec', p.TEXT]

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