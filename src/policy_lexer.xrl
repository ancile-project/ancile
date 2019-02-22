Definitions.

INT        = [0-9]+
ATOM       = [a-zA-Z_]+
WHITESPACE = [\s\t\n\r]


Rules.

0             : {token, {0,  TokenLine}}.
ANYF          : {token, {'anyf',  TokenLine}}.
return        : {token, {'return', TokenLine}}.
{ATOM}        : {token, {atom, TokenLine, TokenChars}}.
\(            : {token, {'(',  TokenLine}}.
\)            : {token, {')',  TokenLine}}.
\[            : {token, {'[',  TokenLine}}.
\]            : {token, {']',  TokenLine}}.
\:            : {token, {':',  TokenLine}}.
\,            : {token, {',',  TokenLine}}.
\.            : {token, {concat,  TokenLine}}.
\+            : {token, {union,  TokenLine}}.
\*            : {token, {star,  TokenLine}}.
\!            : {token, {neg,  TokenLine}}.
\&            : {token, {intersect,  TokenLine}}.
{WHITESPACE}+ : skip_token.
{INT}         : {token, {int,  TokenLine, list_to_integer(TokenChars)}}.

% we will need them for parameters:
%,             : {token, {',',  TokenLine}}.
%\[            : {token, {'[',  TokenLine}}.
%\]            : {token, {']',  TokenLine}}.
%"             : {token, {'"',  TokenLine}}.

Erlang code.

%%