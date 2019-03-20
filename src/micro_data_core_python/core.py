from src.micro_data_core_python.policy_sly import PolicyParser
from src.micro_data_core_python.errors import AncileException
from src.micro_data_core_python.user_specific import UserSpecific
from RestrictedPython import compile_restricted_exec, safe_globals
import inspect


def gen_module_namespace():
    import pkgutil
    import importlib
    import src.micro_data_core_python.functions as base
    from src.micro_data_core_python.functions._config import exclude

    importlib.invalidate_caches()

    prefix_name = base.__name__ + '.'

    # This slightly gross comprehension creates a dictionary with the module name
    # and the imported module for all modules (NOT PACKAGES) in the given base package
    # excludes any module mentioned in the exclude list (see functions._config.py)
    return { mod_name: importlib.import_module(prefix_name + mod_name) 
        for _, mod_name, is_pac in pkgutil.iter_modules(path=base.__path__) 
        if not is_pac and mod_name not in exclude}


def execute(policies, program, sensitive_data=None):
    parsed_policies = dict()
    for provider, policy in policies.items():
        parsed_policies[provider] = PolicyParser.parse_it(policy)

    # We need
    user_specific = UserSpecific(parsed_policies, sensitive_data)

    print(f'\nparsed policies: {UserSpecific._user_policies}')
    program = program
    print(f'submitted program:\n{program}\n')
    result = []

    compile_results = compile_restricted_exec(program)

    if compile_results.errors:
        raise AncileException(compile_results.errors)

    glbls = safe_globals.copy()
    lcls = {'result':result, 'user_specific': user_specific} # Probably need a User info struct here
    lcls.update(gen_module_namespace())

    exec(program, glbls, lcls)

    ## Probably want to do some error checking here
    return result


if __name__ == '__main__':
    policies = {'https://campusdataservices.cs.vassar.edu': 'get_data.asdf.qwer.keep_keys.return_data'}
    user_tokens = {'https://campusdataservices.cs.vassar.edu':'CiISkjBh2RIOj8ivQeoPQ4RPj1IrTJaTIvx2lKeJf8'}
    program  = '''


dp_1 = user_specific.get_empty_data_pair(data_source='https://campusdataservices.cs.vassar.edu')
provider_interaction.get_data(data=dp_1, 
    target_url='https://campusdataservices.cs.vassar.edu/api/last_known')


general.asdf(data=dp_1)
general.qwer(data=dp_1)
general.keep_keys(data=dp_1, keys=['latitude', 'longitude'])
result.append(use_type.return_data(data=dp_1))

'''        

    res = execute(policies,program,sensitive_data=user_tokens)

    print(f'POLICY EVALUATED TO {res}\n')

