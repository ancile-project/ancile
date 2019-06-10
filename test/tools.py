from src.micro_data_core_python.policy_sly import PolicyParser
from src.micro_data_core_python.datapolicypair import DataPolicyPair
from src.micro_data_core_python.decorators import transform_decorator, use_type_decorator
from RestrictedPython import compile_restricted_exec, safe_builtins
from src.micro_data_core_python.errors import PolicyError
from src.micro_data_core_python.core import gen_module_namespace
from src.micro_data_core_python.collection import Collection


def get_dummy_pair(input_policy: str, id_num) -> DataPolicyPair:
    policy = PolicyParser.parse_it(input_policy)
    return DataPolicyPair(policy, None, str(id_num), None, None)

def gen_dummy_fn(name):
    def fn(**kwargs):
        pass
    fn.__name__ = name
    return transform_decorator(fn)


@use_type_decorator
def ret(**kwargs):
    pass

@transform_decorator
def edit(data, key, value):
    data[key] = value

def display(data):
    print(data._data)

def run_test(program: str, *input_policies) -> bool:
    lcls = {f'dp{index}': get_dummy_pair(policy, index)
            for index, policy in enumerate(input_policies)}
    lcls.update(gen_module_namespace())
    lcls['ret'] = ret
    lcls['edit'] = edit
    lcls['Collection'] = Collection
    lcls['display'] = display
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
                lcls.update({f'dp{index}': get_dummy_pair(policy, index)
                             for index, policy in enumerate(input_policies)})
        except (ValueError, PolicyError) as e:
            return False
