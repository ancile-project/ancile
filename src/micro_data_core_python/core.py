from src.micro_data_core_python.policy_sly import PolicyParser
from src.micro_data_core_python.functions import AncileException
from src.micro_data_core_python.user_specific import UserSpecific
from RestrictedPython import compile_restricted_exec, safe_globals
import inspect


def gen_valid_class_namespace():
    import src.micro_data_core_python.functions 
    return {m[0]: m[1] for m in inspect.getmembers(src.micro_data_core_python.functions, inspect.isclass) 
                if m[1].__module__ == 'src.micro_data_core_python.functions'}

def execute(policies, program, sensitive_data=None):
    parsed_policies = dict()
    for provider, policy in policies.items():
        parsed_policies[provider] = PolicyParser.parse_it(policy)

    # THIS WILL GET CHANGED
    UserSpecific._user_policies = parsed_policies
    UserSpecific._user_tokens = sensitive_data

    print(f'\nparsed policies: {UserSpecific._user_policies}')
    program = program
    print(f'submitted program:\n{program}\n')
    result = []

    compile_results = compile_restricted_exec(program)

    if compile_results.errors:
        raise AncileException(compile_results.errors)
    
    glbls = safe_globals.copy()
    lcls = {'result':result} # Probably need a User info struct here
    lcls.update(gen_valid_class_namespace())

    exec(program, glbls, lcls)

    ## Probably want to do some error checking here
    return result


if __name__ == '__main__':
    policies = {'https://campusdataservices.cs.vassar.edu': b'get_data.asdf.qwer.keep_keys.return_data'}
    user_tokens = {'https://campusdataservices.cs.vassar.edu':'CiISkjBh2RIOj8ivQeoPQ4RPj1IrTJaTIvx2lKeJf8'}
    program  = '''

def return_data(data=None):
    return data

dp_1 = DataIngress.get_empty_data_pair('https://campusdataservices.cs.vassar.edu')
DataIngress.get_data(data=dp_1, 
    target_url='https://campusdataservices.cs.vassar.edu/api/last_known',
    data_source='https://campusdataservices.cs.vassar.edu')



Transformation.asdf(data=dp_1)
Transformation.qwer(data=dp_1)
Transformation.keep_keys(data=dp_1, keys=['latitude', 'longitude'])
result.append(DataEgress.return_data(data=dp_1))

'''        

    res = execute(policies,program,sensitive_data=user_tokens)

    print(f'POLICY EVALUATED TO {res}\n')

