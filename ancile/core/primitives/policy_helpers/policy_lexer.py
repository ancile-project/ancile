from sly import Lexer


class PolicyLexer(Lexer):
    tokens = { TEXT, NUMBER, FLOAT, UNION, CONCAT, INTERSECT,  NEG, STAR,
               ANYF, LPAREN, RPAREN, LBRACKET, RBRACKET, COMMA, EQ,
               PRIVATE, STRING, NEQ, LEQ, LE, GEQ, GE, LBRACE, RBRACE, IN,
               TRUE, FALSE }
    ignore = ' \t\n\r\f\v'


    # Tokens
    TEXT = r'[a-zA-Z_][a-zA-Z0-9_]*'

    @_(r'[-]?\d+\.\d+')
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'[-]?\d+')
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