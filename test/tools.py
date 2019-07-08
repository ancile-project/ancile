from ancile_core.policy_sly import PolicyParser
from ancile_core.datapolicypair import DataPolicyPair
from ancile_core.decorators import transform_decorator, use_type_decorator
from RestrictedPython import compile_restricted_exec, safe_builtins
from ancile_web.errors import PolicyError
from ancile_core.core import gen_module_namespace
from ancile_core.collection import Collection


def get_dummy_pair(input_policy: str, id_num) -> DataPolicyPair:
    policy = PolicyParser.parse_it(input_policy)
    return DataPolicyPair(policy, None, str(id_num), str(id_num), None)

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

    return data

@transform_decorator
def double(data, key):
    data[key] *= 2

    return data

def display(data):
    print(data._data)

def run_test(program: str, *input_policies) -> bool:
    lcls = {f'dp{index}': get_dummy_pair(policy, index)
            for index, policy in enumerate(input_policies)}
    lcls.update(gen_module_namespace())
    lcls['ret'] = ret
    lcls['edit'] = edit
    lcls['double'] = double
    lcls['Collection'] = Collection
    lcls['display'] = display
    lcls['test'] = gen_dummy_fn('test')
    lcls['filter'] = gen_dummy_fn('filter')
    lcls['view'] = gen_dummy_fn('view')
    glbls = {'__builtins__': safe_builtins}

    while True:
        try:
            compile_results = compile_restricted_exec(program)
            if compile_results.errors:
                raise Exception
            else:
                exec(compile_results.code, glbls, lcls)

                return True

        except PolicyError as e:
            return False
