Definitions.

INT        = [0-9]+
TEXT       = [a-zA-Z_]+
WHITESPACE = [\s\r\t\n]
C   = (<|<=|=|=>|>)



Rules.
%\t          : {token, {tab,  TokenLine}}.
;         : {token, {';',  TokenLine}}.
:=        : {token, {':=',  TokenLine}}.
if        : {token, {'if',  TokenLine}}.
else        : {token, {'else',  TokenLine}}.
do        : {token, {'do',  TokenLine}}.
end        : {token, {'end',  TokenLine}}.
while      : {token, {'while',  TokenLine}}.
for      : {token, {'for',  TokenLine}}.
to      : {token, {'to',  TokenLine}}.
print    : {token, {'print',  TokenLine}}.
{TEXT}      : {token, {text, TokenLine, TokenChars}}.
{WHITESPACE}+ : skip_token.
{C}         : {token, {comparison, TokenLine, TokenChars}}.
{INT}         : {token, {int,  TokenLine, list_to_integer(TokenChars)}}.

% will need later for params
%\(            : {token, {'(',  TokenLine}}.
%\)            : {token, {')',  TokenLine}}.
%,             : {token, {',',  TokenLine}}.

Erlang code.

%%