from ancile.core.primitives.policy_helpers.policy_parser import PolicyParser
from ancile.core.decorators import *
from ancile.core.primitives import *
from RestrictedPython import compile_restricted_exec, safe_builtins
from ancile.utils.errors import PolicyError
from ancile.core.context_building import gen_module_namespace

import traceback

def get_dummy_pair(input_policy: str, id_num) -> DataPolicyPair:
    policy = PolicyParser.parse_it(input_policy)
    dp = DataPolicyPair(policy, None, str(id_num), str(id_num), None)
    dp._data = dict()
    return dp

def gen_dummy_fn(name):
    @TransformDecorator()
    def fn(**kwargs):
        pass
    fn.__name__ = name
    return fn


@UseDecorator()
def ret(**kwargs):
    pass

@TransformDecorator()
def edit(data, key, value):
    data[key] = value

    return data

@TransformDecorator()
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
                raise Exception(compile_results.errors)
            else:
                exec(compile_results.code, glbls, lcls)

                return True

        except:
            print(traceback.format_exc())
            return False
