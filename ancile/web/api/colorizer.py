from enum import Enum
from ancile.core.context_building import gen_module_namespace
from ancile.core.primitives.policy_helpers.expressions import *
from ancile.core.primitives.policy_helpers.policy_parser import PolicyParser
import inspect


def find_function(function_name):
    return [
        fn
        for _key, module in gen_module_namespace().items()
        for fn_name, fn in module.__dict__.items()
        if fn_name == function_name
    ]


class FuncType(Enum):
    NONE = 0
    FETCH = 1
    TRANSFORM = 2
    AGGREGATE = 3
    REDUCE = 4
    RETURN = 5
    COLLECTION = 6
    CONDITION = 7


def dec_string_to_type(string: str) -> FuncType:
    if "ExternalDecorator" in string:
        return FuncType.FETCH
    elif "TransformDecorator" in string:
        return FuncType.TRANSFORM
    elif "UseDecorator" in string or string == "return_to_app":
        return FuncType.RETURN
    elif "ComparisonDecorator" in string:
        return FuncType.CONDITION
    elif "AggregateDecorator" in string:
        return FuncType.AGGREGATE
    elif "ReductionDecorator" in string:
        return FuncType.REDUCE
    elif "add_to_collection" == string:
        return FuncType.COLLECTION
    else:
        return FuncType.NONE


def get_fn_type(function_name):
    if function_name == "add_to_collection":
        return FuncType.COLLECTION
    elif function_name in ["return_to_app", "append_dp_data_to_result"]:
        return FuncType.RETURN
    elif function_name in ["_enforce_comparison", "_test_false", "_test_true"]:
        return FuncType.CONDITION

    function_list = find_function(function_name)
    if function_list == []:
        return FuncType.NONE

    # get the decorator name w/o leading @ and convert to an enum
    types = [
        dec_string_to_type(x[1:])
        for x in (inspect.getsource(fn).split()[0] for fn in function_list)
    ]

    # multiple definitions are fine if they agree
    if all((x == types[0] for x in types)):
        return types[0]
    else:
        # Otherwise give up
        return FuncType.NONE


def annotate(parsed):
    if type(parsed) == ExecExpression:
        name = parsed.policy_command
        parsed.type = get_fn_type(name)
    elif isinstance(parsed, UnaryExpression):
        annotate(parsed.expression)
    elif isinstance(parsed, BinaryExpression):
        annotate(parsed.l_expr)
        annotate(parsed.r_expr)

def parse_annotated(policy_text):
    parsed = PolicyParser.parse_it(policy_text)
    annotate(parsed)
    return parsed