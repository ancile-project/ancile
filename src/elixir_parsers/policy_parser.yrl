Nonterminals
method params param
clause func.

Terminals
'[' ']' '(' ')' ':' ','
text int anyf float string
concat union intersect star neg 0 return.

Rootsymbol clause.

clause -> neg clause : [neg, '$2'].
clause -> clause star : [star, '$1'].
clause -> clause concat clause : [concat, '$1', '$3']. % to simplify syntax

clause -> neg '[' clause ']' : [neg, '$3'].
clause -> '[' clause ']' star : [star, '$2'].
clause -> '[' clause concat clause ']' : [concat, '$2', '$4'].
clause -> '[' clause union clause ']' : [union, '$2', '$4'].
clause -> '[' clause intersect clause ']' : [intersect, '$2', '$4'].

clause -> func : '$1'.

func -> return: [exec, return].
func -> anyf : [exec, anyf].
func -> 0 : 0.
func -> method : [exec, '$1'].
func -> text : [exec, {extract_token('$1'),  {params, []} }].

method -> text '(' ')' : {extract_token('$1'),  {params, []}}.
method -> text '(' params ')' : {extract_token('$1'), {params, '$3'}}.
params -> param ',' params : ['$1' | '$3'].
params -> param : ['$1'].
param -> text ':' int: [extract_token('$1'), extract_token('$3')].
param -> text ':' string: [extract_token('$1'), extract_token('$3')].
param -> text ':' float: [extract_token('$1'), extract_token('$3')].


Erlang code.

extract_token({_Token, _Line, Value}) -> Value.