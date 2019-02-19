Definitions.

INT        = [0-9]+
ATOM       = [a-zA-Z_]+
WHITESPACE = [\s\t\r]
C   = (<|<=|=|=>|>)



Rules.
\n          : {token, {end_command,  TokenLine}}.
{ATOM}      : {token, {atom, TokenLine, TokenChars}}.
{WHITESPACE}+ : skip_token.

% will need later for params
%{INT}         : {token, {int,  TokenLine, list_to_integer(TokenChars)}}.
%\(            : {token, {'(',  TokenLine}}.
%\)            : {token, {')',  TokenLine}}.
%,             : {token, {',',  TokenLine}}.

Erlang code.

%%