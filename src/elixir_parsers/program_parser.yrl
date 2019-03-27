Nonterminals

prog subprog val method params param
if_clause while_clause assign for_clause
clause.

Terminals

text int ';' ',' ':' '(' ')'
'if' 'while' 'for' 'to' 'return'
'do' 'end' ':=' string float 'else'
comparison.

Rootsymbol prog.

prog -> subprog prog : ['$1' | '$2'].
prog -> subprog : ['$1'].

subprog -> 'return' ';': [exec, return].
subprog -> text ';' : [exec, {extract_token('$1'),  {params, []} }].
subprog -> method ';' : [exec, '$1'].
subprog -> if_clause: '$1'.
subprog -> while_clause : '$1'.
subprog -> assign ';': '$1'.
subprog -> for_clause : '$1'.

if_clause -> 'if' clause 'do' prog 'end' : ['if', '$2', '$4'].
if_clause -> 'if' clause 'do' prog 'else' prog 'end' : ['if', '$2', '$4', '$6'].
while_clause -> 'while' clause 'do' prog 'end' : ['while', '$2', '$4'].
for_clause ->
        'for' text ':=' int 'to' int 'do' prog 'end' :
            ['for', [assign, extract_token('$2'), extract_token('$4')],
            [to, extract_token('$6')], '$8'].
clause -> text comparison val : [comp, extract_token('$2'), extract_token('$1'), '$3'].

assign -> text ':=' val : [assign, extract_token('$1'), '$3'].
assign -> text ':=' method : [assign, extract_token('$1'), '$3'].

method -> text '(' ')' : {extract_token('$1'),  {params, []}}.
method -> text '(' params ')' : {extract_token('$1'), {params, '$3'}}.
params -> param ',' params : ['$1' | '$3'].
params -> param : ['$1'].
param -> text ':' int: [extract_token('$1'), extract_token('$3')].
param -> text ':' string: [extract_token('$1'), extract_token('$3')].
param -> text ':' float: [extract_token('$1'), extract_token('$3')].

val -> text : extract_token('$1').
val -> int : extract_token('$1').
val -> string : extract_token('$1').
val -> float : extract_token('$1').

Erlang code.

extract_token({_Token, _Line, Value}) -> Value.