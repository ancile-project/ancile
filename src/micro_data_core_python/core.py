from src.micro_data_core_python.policy_sly import PolicyParser
from src.micro_data_core_python.errors import AncileException
from src.micro_data_core_python.user_specific import UserSpecific
from src.micro_data_core_python.result import Result
from RestrictedPython import compile_restricted_exec, safe_globals
import uuid
import pickle
import traceback
import redis

r = redis.Redis(host='localhost', port=6379, db=0)


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
    return {mod_name: importlib.import_module(prefix_name + mod_name)
            for _, mod_name, is_pac in pkgutil.iter_modules(path=base.__path__)
            if not is_pac and mod_name not in exclude}


def assemble_locals(result, user_specific):
    locals = gen_module_namespace()
    locals['result'] = result
    locals['user_specific'] = user_specific
    return locals


# We check if policies finished and otherwise save them.
def save_dps(user_specific):
    dps_to_save = user_specific._active_dps
    active_dps = dict()
    for name, dp in dps_to_save.items():
        # nothing left to execute:
        if dp._policy in [0, 1]:
            continue
        else:
            print(f'There is a policy not finished: {dp._policy}')
            active_dps[name] = dp

    if active_dps:
        iid = str(uuid.uuid1())
        pickled_dps = pickle.dumps(active_dps)
        r.set(iid, pickled_dps)
        return iid
    else:
        return None


def retrieve_dps(persisted_dp_uuid):
    print("Retrieving previously used Data Policy Pairs")
    dp_pairs = r.get(persisted_dp_uuid)
    if dp_pairs:
        return pickle.loads(dp_pairs)
    else:
        raise AncileException("Your UUID is invalid. Supply correct UUID or "
                              "leave the field empty.")



def execute(policies, program, sensitive_data=None, persisted_dp_uuid=None):
    json_output = dict()
    # object to interact with the program
    result = Result()

    parsed_policies = PolicyParser.parse_policies(policies)
    user_specific = UserSpecific(parsed_policies, sensitive_data)
    print(user_specific._active_dps)

    if persisted_dp_uuid:
        user_specific._active_dps = retrieve_dps(persisted_dp_uuid)

    glbls = safe_globals.copy()
    lcls = assemble_locals(result=result, user_specific=user_specific)
    try:
        compile_results = compile_restricted_exec(program)
        if compile_results.errors:
            raise AncileException(compile_results.errors)
        exec(program, glbls, lcls)
    except:
        print(traceback.format_exc())
        return {'result': 'error', 'traceback': traceback.format_exc()}

    json_output['persisted_dp_uuid'] = save_dps(user_specific)
    json_output['data'] = result._dp_pair_data
    json_output['result'] = 'ok'

    return json_output


if __name__ == '__main__':
    policies = {'https://campusdataservices.cs.vassar.edu': 'get_data.in_geofences.append_dp_data_to_result'}
    user_tokens = {'https://campusdataservices.cs.vassar.edu': {'access_token': 'CiISkjBh2RIOj8ivQeoPQ4RPj1IrTJaTIvx2lKeJf8'}}
    program1 = '''
dp_1 = user_specific.get_empty_data_pair(data_source='https://campusdataservices.cs.vassar.edu')
provider_interaction.get_data(data=dp_1, 
    target_url='https://campusdataservices.cs.vassar.edu/api/last_known')

'''

    res = execute(policies, program1, sensitive_data=user_tokens)
    print(f'Result of the first call: {res}')
    if res['result'] != 'error':


        program2 = '''
dp_1 = user_specific.retrieve_existing_dp_pair(data_source='https://campusdataservices.cs.vassar.edu')
fences = [
{"label":"Library", "longitude": -73.8977594,
  "latitude": 41.6872415, "radius": 100},
{"label":"Quad", "longitude": -73.8969219, 
  "latitude": 41.6889501, "radius": 100},
{"label":"Main", "longitude": -73.8952052,
  "latitude": 41.6868915, "radius": 100} ]

vassar_location.in_geofences(geofences=fences, data=dp_1)
# general.keep_keys(data=dp_1, keys=['in_geofences'])
result.append_dp_data_to_result(data=dp_1)

        '''

        res = execute(policies, program2, sensitive_data=user_tokens, persisted_dp_uuid=res['persisted_dp_uuid'])

        print(f'POLICY EVALUATED TO {res}\n')
