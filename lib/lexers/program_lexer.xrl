Definitions.

INT        = [0-9]+
ATOM       = [a-z_]+
WHITESPACE = [\s\t\n\r]
C   = (<|<=|=|=>|>)



Rules.
%! TODO
;\n           : {token, {:next_line,  TokenLine}}.
{INT}         : {token, {int,  TokenLine, list_to_integer(TokenChars)}}.
{ATOM}        : {token, {atom, TokenLine, TokenChars}}.
\(            : {token, {'(',  TokenLine}}.
\)            : {token, {')',  TokenLine}}.
,             : {token, {',',  TokenLine}}.
{WHITESPACE}+ : skip_token.

Erlang code.

%%