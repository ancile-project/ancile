Definitions.

NUM        = [+-]?[0-9]+
TEXT       = [a-zA-Z_]+
WHITESPACE = [\s\r\t\n]
C          = (<|<=|=|!=|=>|>)
FLOAT      = {NUM}.{NUM}
STRING     = "[0-9a-zA-Z!#%&'()*+,-./:;<=>?[\]^_{|}~\s\t]*"


Rules.
%\t          : {token, {tab,  TokenLine}}.
;             : {token, {';',  TokenLine}}.
:=            : {token, {':=',  TokenLine}}.
\(            : {token, {'(',  TokenLine}}.
\)            : {token, {')',  TokenLine}}.
\:            : {token, {':',  TokenLine}}.
\,            : {token, {',',  TokenLine}}.
if            : {token, {'if',  TokenLine}}.
else          : {token, {'else',  TokenLine}}.
do            : {token, {'do',  TokenLine}}.
end           : {token, {'end',  TokenLine}}.
while         : {token, {'while',  TokenLine}}.
for           : {token, {'for',  TokenLine}}.
to            : {token, {'to',  TokenLine}}.
print         : {token, {'print',  TokenLine}}.
return        : {token, {'return', TokenLine}}.
{TEXT}        : {token, {text, TokenLine, TokenChars}}.
{WHITESPACE}+ : skip_token.
{C}           : {token, {comparison, TokenLine, TokenChars}}.
{NUM}         : {token, {int,  TokenLine, list_to_integer(TokenChars)}}.
{FLOAT}       : {token, {float, TokenLine, list_to_float(TokenChars)}}.
{STRING}      : {token, {string, TokenLine, string:strip(TokenChars, both, $")}}.

% will need later for params
%\(            : {token, {'(',  TokenLine}}.
%\)            : {token, {')',  TokenLine}}.
%,             : {token, {',',  TokenLine}}.

Erlang code.

%%