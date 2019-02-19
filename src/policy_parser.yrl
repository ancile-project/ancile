Nonterminals clause func.
Terminals '(' ')' atom anyf concat union star neg 0.
Rootsymbol clause.

clause -> neg clause : [neg, '$2'].
clause -> clause star : [star, '$1'].
clause -> clause concat clause : [concat, '$1', '$3']. % to simplify syntax

clause -> neg '(' clause ')' : [neg, '$3'].
clause -> '(' clause ')' star : [star, '$2'].
clause -> '(' clause concat clause ')' : [concat, '$2', '$4'].
clause -> '(' clause union clause ')' : [union, '$2', '$4'].
clause -> func : '$1'.


func -> anyf : [exec, extract_token_name('$1')].
func -> 0 : extract_token_name('$1').
func -> atom : [exec, extract_token('$1')].


Erlang code.

extract_token({_Token, _Line, Value}) -> Value.
extract_token_name({Token, _Line}) -> Token.