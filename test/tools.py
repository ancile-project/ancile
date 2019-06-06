from src.micro_data_core_python.policy_sly import PolicyParser
from src.micro_data_core_python.datapolicypair import DataPolicyPair
from src.micro_data_core_python.decorators import transform_decorator, use_type_decorator
from RestrictedPython import compile_restricted_exec, safe_builtins
from src.micro_data_core_python.errors import PolicyError


def get_dummy_pair(input_policy: str) -> DataPolicyPair:
    policy = PolicyParser.parse_it(input_policy)
    return DataPolicyPair(policy, None, None, None, None)


def gen_dummy_fn(name):
    def fn(**kwargs):
        pass
    fn.__name__ = name
    return transform_decorator(fn)


@use_type_decorator
def ret(**kwargs):
    pass


def run_test(input_policy: str, program: str) -> bool:
    lcls = {'dp': get_dummy_pair(input_policy),
            'ret': ret}
    glbls = {'__builtins__': safe_builtins}

    while True:
        try:
            try:
                compile_results = compile_restricted_exec(program)
                if compile_results.errors:
                    raise Exception
                else:
                    exec(compile_results.code, glbls, lcls)

                    return True
            except NameError as e:
                fn_name = e.args[0].split('\'')[1]
                lcls[fn_name] = gen_dummy_fn(fn_name)
                lcls['dp'] = get_dummy_pair(input_policy)
        except (ValueError, PolicyError) as e:
            return False
