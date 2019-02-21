Nonterminals

prog val
if_clause while_clause assign for_clause
clause.

Terminals

text int ';'
'if' 'while' 'for' 'to'
'do' 'end' ':='
comparison.

Rootsymbol prog.

prog -> text ';' : [[exec, extract_token('$1')]].
prog -> text ';' prog : [[exec, extract_token('$1')] | '$3'].

prog -> if_clause : ['$1'].
prog -> while_clause : ['$1'].
prog -> assign ';': ['$1'].
prog -> for_clause : ['$1'].

if_clause -> 'if' clause 'do' prog 'end' : ['if', '$2', '$4'].
while_clause -> 'while' clause 'do' prog 'end' : ['while', '$2', '$4'].
for_clause ->
        'for' text ':=' int 'to' int 'do' prog 'end' :
            ['for', [assign, extract_token('$2'), extract_token('$4')],
            [to, extract_token('$6')], '$8'].
clause -> text comparison val : [comp, extract_token('$2'), extract_token('$1'), '$3'].

assign -> text ':=' val : [assign, extract_token('$1'), '$3'].

val -> text : extract_token('$1').
val -> int : extract_token('$1').

Erlang code.

extract_token({_Token, _Line, Value}) -> Value.