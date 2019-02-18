Nonterminals prog.
Terminals atom end_command.
Rootsymbol prog.

prog -> atom end_command prog : [extract_token('$1') | '$3'].
prog -> atom : [extract_token('$1')].


Erlang code.

extract_token({_Token, _Line, Value}) -> Value.