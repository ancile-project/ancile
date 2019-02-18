Definitions.

INT        = [0-9]+
ATOM       = [a-z_]+
WHITESPACE = [\s\t\n\r]


Rules.

0             : {token, {0,  TokenLine}}.
ANYF          : {token, {anyf,  TokenLine}}.
{INT}         : {token, {int,  TokenLine, list_to_integer(TokenChars)}}.
{ATOM}        : {token, {atom, TokenLine, TokenChars}}.
\(            : {token, {'(',  TokenLine}}.
\)            : {token, {')',  TokenLine}}.
\.            : {token, {concat,  TokenLine}}.
\+            : {token, {union,  TokenLine}}.
\*            : {token, {star,  TokenLine}}.

% we need them for parameters:
,             : {token, {',',  TokenLine}}.
\[            : {token, {'[',  TokenLine}}.
\]            : {token, {']',  TokenLine}}.
"             : {token, {'"',  TokenLine}}.
{WHITESPACE}+ : skip_token.

Erlang code.

%%