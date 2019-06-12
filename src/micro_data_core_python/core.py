from src.micro_data_core_python.datapolicypair import DataPolicyPair, PrivateData
from src.micro_data_core_python.policy_sly import PolicyParser
from src.micro_data_core_python.errors import AncileException
from src.micro_data_core_python.user_specific import UserSpecific
from src.micro_data_core_python.result import Result
from src.micro_data_core_python.storage import store as _store, load
from src.micro_data_core_python.policy import Policy
from RestrictedPython import compile_restricted_exec, safe_globals, limited_builtins, safe_builtins
import uuid
import pickle
import traceback
import redis
from collections import namedtuple
import yaml
from src.micro_data_core_python.utils import *
from src import configs
from src.secret import REDIS_CONFIG

with open('./config/secret.yaml', 'r') as f:
    config = yaml.safe_load(f)


UserInfoBundle = namedtuple("UserInfoBundle", ['username', 'policies',
                                               'tokens', 'private_data'])

r = redis.Redis(**REDIS_CONFIG)


def gen_module_namespace():
    import pkgutil
    import importlib
    import src.micro_data_core_python.functions as base
    from src.micro_data_core_python.functions._config import exclude

    importlib.invalidate_caches()

    prefix_name = base.__name__ + '.'

    # This slightly gross comprehension creates a dictionary with the module
    # name and the imported module for all modules (NOT PACKAGES) in the given
    # base package excludes any module mentioned in the exclude list
    # (see functions._config.py)
    return {mod_name: importlib.import_module(prefix_name + mod_name)
            for _, mod_name, is_pac in pkgutil.iter_modules(path=base.__path__)
            if not is_pac and mod_name not in exclude}


def assemble_locals(result, user_specific, app_id, user_info, purpose):
    from src.micro_data_core_python.decorators import store_decorator
    locals = gen_module_namespace()

    def user(name: str) -> UserSpecific:
        return user_specific[name]

    def store(obj):
        result._stored_keys[obj.__name__] = _store(obj)

    locals['result'] = result
    locals['store'] = store
    locals['load'] = load
    locals['private'] = PrivateData
    locals['user'] = user
    return locals

# We check if policies finished and otherwise save them.
# def save_dps(users_specific):
#     active_dps = dict()
#     encryption_keys = dict()
#     encrypted_data = dict()
#     redis_persist = False

#     for username, user_specific in users_specific.items():
#         dps_to_save = user_specific._active_dps
#         if active_dps.get(username, False) is False:
#             active_dps[username] = dict()
#             encryption_keys[username] = dict()
#             encrypted_data[username] = dict()

#         for name, dp in dps_to_save.items():

#             # nothing left to execute:
#             # print(f'name: {name}, policy: {dp._policy}')
#             if dp._policy.e_step() == 1:
#                 if dp._encryption_keys:
#                     encryption_keys[username][name] = dp._encryption_keys
#             else:
#                 redis_persist = True
#                 if config.get('encrypt', False):
#                     # print(f'There is a policy not finished: {dp._policy}. Encrypting fields.')
#                     keys_dict, enc_dp = encrypt(dp._data)
#                     # print(keys_dict)
#                     # print(enc_dp)
#                     dp._encryption_keys.update(keys_dict)
#                     dp._data = {'output': []}
#                     active_dps[username][name] = dp
#                     encrypted_data[username][name] = enc_dp
#                 else:
#                     # print(f'There is a policy not finished: {dp._policy}. Saving data.')
#                     active_dps[username][name] = dp

#     # print(f'active dps {active_dps.keys()}')
#     iid = None
#     if redis_persist:
#         iid = str(uuid.uuid1())
#         pickled_dps = pickle.dumps(active_dps)
#         r.set(iid, pickled_dps, ex=3600)

#     return iid, encrypted_data, encryption_keys


# def retrieve_dps(persisted_dp_uuid, users_specific, app_id):
#     # print("Retrieving previously used Data Policy Pairs")
#     dp_pairs = r.get(persisted_dp_uuid)
#     if dp_pairs:
#         active_dps = pickle.loads(dp_pairs)
#         for username in active_dps.keys():
#             if active_dps.get(username, False) is False:
#                 raise AncileException(f"active_dps don't have a user: {username}. Available names: "
#                                       f"{list(active_dps.keys())}.")
#             if users_specific.get(username, False) is False:
#                 new_us = UserSpecific(policies=None, tokens=None, 
#                                       private_data=None, username=username,
#                                       app_id=app_id)
#                 users_specific[username] = new_us
#             users_specific[username]._active_dps = active_dps[username]

#     else:
#         raise AncileException("Your UUID is invalid. Supply correct UUID or "
#                               "leave the field empty.")

def retrieve_compiled(program):
    import dill
    redis_response = r.get(program) if configs.enable_cache else None

    if redis_response is None:
        compile_results = compile_restricted_exec(program)
        if compile_results.errors:
            raise AncileException(compile_results.errors)
        if configs.enable_cache:
            r.set(program, dill.dumps(compile_results.code), ex=600)

        return compile_results.code
    print("USED CACHED PROGRAM")
    return dill.loads(redis_response)


def execute(user_info, program, persisted_dp_uuid=None, app_id=None,
            purpose=None):
    json_output = dict()
    # object to interact with the program
    result = Result()
    users_specific = dict()
    for user in user_info:
        parsed_policies = PolicyParser.parse_policies(user.policies)
        user_specific = UserSpecific(parsed_policies, user.tokens,
                                     user.private_data,
                                     username=user.username,
                                     app_id=app_id)
        users_specific[user.username] = user_specific
        # print(user_specific._active_dps)

    # if persisted_dp_uuid:
    #     retrieve_dps(persisted_dp_uuid, users_specific, app_id)

    glbls = {'__builtins__': safe_builtins}
    lcls = assemble_locals(result=result, user_specific=users_specific,
                           app_id=app_id, user_info=user_info,
                           purpose=purpose)
    try:
        c_program = retrieve_compiled(program)
        exec(c_program, glbls, lcls)
        json_output['persisted_dp_uuid'], encrypted_data, encryption_keys = save_dps(users_specific)
        if config.get('encrypt', False):
            json_output['encrypted_data'] = encrypted_data
            json_output['encryption_keys'] = encryption_keys

        if persisted_dp_uuid:
            r.delete(persisted_dp_uuid)
    except:
        # print(traceback.format_exc())
        json_output = {'result': 'error', 'traceback': traceback.format_exc()}
        if persisted_dp_uuid:
            json_output[persisted_dp_uuid] = persisted_dp_uuid
        return json_output

    json_output['data'] = result._dp_pair_data
    json_output['result'] = 'ok'

    return json_output
