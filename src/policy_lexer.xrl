Definitions.

NUM        = [-+]?[0-9]+
TEXT       = [a-zA-Z_]+
WHITESPACE = [\s\t\n\r]
FLOAT      = [-+]?[0-9]+\.[0-9]+
STRING     = "[0-9a-zA-Z!#%&'()\*+,-\./:;<=>?[\]^_{|}~\s\t]*"


Rules.

0             : {token, {0,  TokenLine}}.
ANYF          : {token, {'anyf',  TokenLine}}.
return        : {token, {'return', TokenLine}}.
{TEXT}        : {token, {text, TokenLine, TokenChars}}.
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
{NUM}         : {token, {int,  TokenLine, list_to_integer(TokenChars)}}.
{FLOAT}       : {token, {float, TokenLine, list_to_float(TokenChars)}}.
{STRING}      : {token, {string, TokenLine, string:strip(TokenChars, both, $")}}.

% we will need them for parameters:
%,             : {token, {',',  TokenLine}}.
%\[            : {token, {'[',  TokenLine}}.
%\]            : {token, {']',  TokenLine}}.
%"             : {token, {'"',  TokenLine}}.

Erlang code.

%%