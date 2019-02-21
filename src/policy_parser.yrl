Nonterminals clause func.
Terminals '(' ')' atom anyf concat union intersect star neg 0 return.
Rootsymbol clause.

clause -> neg clause : [neg, '$2'].
clause -> clause star : [star, '$1'].
clause -> clause concat clause : [concat, '$1', '$3']. % to simplify syntax

clause -> neg '(' clause ')' : [neg, '$3'].
clause -> '(' clause ')' star : [star, '$2'].
clause -> '(' clause concat clause ')' : [concat, '$2', '$4'].
clause -> '(' clause union clause ')' : [union, '$2', '$4'].
clause -> '(' clause intersect clause ')' : [intersect, '$2', '$4'].
clause -> func : '$1'.

func -> return: [exec, return].
func -> anyf : [exec, anyf].
func -> 0 : 0.
func -> atom : [exec, extract_token('$1')].


Erlang code.

extract_token({_Token, _Line, Value}) -> Value.