from ancile_core.datapolicypair import DataPolicyPair, PrivateData
from ancile_core.policy_sly import PolicyParser
from ancile_web.errors import AncileException
from ancile_core.user_specific import UserSpecific
from ancile_core.result import Result
from ancile_core.storage import store as _store, load as _load, del_key, gen_key
from ancile_core.policy import Policy
from RestrictedPython import compile_restricted_exec, safe_globals, limited_builtins, safe_builtins
from ancile_core.collection import Collection
import traceback
import redis
from collections import namedtuple
import yaml
from ancile_core.utils import *
from config.loader import REDIS_CONFIG, ENABLE_CACHE
import logging
logger = logging.getLogger(__name__)

UserInfoBundle = namedtuple("UserInfoBundle", ['username', 'policies',
                                               'tokens', 'private_data'])

r = redis.Redis(**REDIS_CONFIG)


def gen_module_namespace():
    import pkgutil
    import importlib
    import ancile_core.functions as base
    from ancile_core.functions._config import exclude

    importlib.invalidate_caches()

    prefix_name = base.__name__ + '.'

    # This slightly gross comprehension creates a dictionary with the module
    # name and the imported module for all modules (NOT PACKAGES) in the given
    # base package excludes any module mentioned in the exclude list
    # (see functions._config.py)
    return {mod_name: importlib.import_module(prefix_name + mod_name)
            for _, mod_name, is_pac in pkgutil.iter_modules(path=base.__path__)
            if not is_pac and mod_name not in exclude}


def assemble_locals(result, user_specific, collection_info, app_id):
    lcls = gen_module_namespace()

    def user(name: str) -> UserSpecific:
        return user_specific[name]

    def store(obj, name):
        key = gen_key()
        _store(obj, f'{app_id}:{key}')
        result._stored_keys[name] = key
        if isinstance(obj, DataPolicyPair) and obj._was_loaded:
            del_key(obj._load_key)

    def new_collection():
        return Collection()

    def get_dataset(*users):
        policy = '0'
        for collection in collection_info:
            if all(usr in collection.user_ids for usr in users):
                policy = collection.policy
                break

        return Collection(policy)

    def load(key):
        return _load(f'{app_id}:{key}')

    lcls['result'] = result
    lcls['store'] = store
    lcls['load'] = load
    lcls['private'] = PrivateData
    lcls['user'] = user
    lcls['new_collection'] = new_collection
    return lcls

def retrieve_compiled(program):
    import dill
    redis_response = r.get(program) if ENABLE_CACHE else None

    if redis_response is None:
        compile_results = compile_restricted_exec(program)
        if compile_results.errors:
            raise AncileException(compile_results.errors)
        if ENABLE_CACHE:
            r.set(program, dill.dumps(compile_results.code), ex=600)
            logger.debug("Cache miss on submitted program")
        return compile_results.code
    logger.debug("Used cached program")
    return dill.loads(redis_response)


def execute(user_info, program, persisted_dp_uuid=None, app_id=None,
            purpose=None, collection_info=None):
    json_output = dict()
    # object to interact with the program
    result = Result()
    users_specific = dict()
    for user in user_info:
        user_specific = UserSpecific(user.policies, user.tokens,
                                     user.private_data,
                                     username=user.username,
                                     app_id=app_id)
        users_specific[user.username] = user_specific
        # print(user_specific._active_dps)

    # if persisted_dp_uuid:
    #     retrieve_dps(persisted_dp_uuid, users_specific, app_id)

    glbls = {'__builtins__': safe_builtins}
    lcls = assemble_locals(result=result,
                           user_specific=users_specific,
                           collection_info=collection_info,
                           app_id=app_id)
    try:
        c_program = retrieve_compiled(program)
        exec(c_program, glbls, lcls)
        # json_output['persisted_dp_uuid'], encrypted_data, encryption_keys = save_dps(users_specific)
        # if config.get('encrypt', False):
        #     json_output['encrypted_data'] = encrypted_data
        #     json_output['encryption_keys'] = encryption_keys

        if persisted_dp_uuid:
            r.delete(persisted_dp_uuid)
    except:
        print(traceback.format_exc())
        json_output = {'result': 'error', 'traceback': traceback.format_exc()}
        if persisted_dp_uuid:
            json_output[persisted_dp_uuid] = persisted_dp_uuid
        return json_output
    json_output['stored_items'] = result._stored_keys
    json_output['data'] = result._dp_pair_data
    json_output['result'] = 'ok'

    return json_output
