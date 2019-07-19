from ancile_core.datapolicypair import DataPolicyPair, PrivateData
from ancile_core.policy_sly import PolicyParser
from ancile_web.errors import AncileException
from ancile_core.user_specific import UserSpecific
from ancile_core.result import Result
from ancile_core.storage import store as _store, load as _load, del_key, gen_key, store_encrypted as _encrypt
from ancile_core.policy import Policy
from ancile_core.decorators import use_type_decorator
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


def assemble_locals(result, user_specific, app_id, app_module=None):
    lcls = gen_module_namespace()

    def user(name: str) -> UserSpecific:
        return user_specific[name]

    def store(obj, name):
        key = gen_key()
        _store(obj, f'{app_id}:{key}')
        result._stored_keys[name] = key
        if isinstance(obj, DataPolicyPair) and obj._was_loaded:
            del_key(obj._load_key)

    def encrypt(obj, name):
        key = gen_key()
        encrypted_data = _encrypt(obj, f'{app_id}:{key}')
        result._stored_keys[name] = key
        result._encrypted_data[name] = encrypted_data

    def new_collection():
        return Collection()

    def load(key):
        return _load(f'{app_id}:{key}')

    @use_type_decorator
    def return_to_app(data, encryption_keys, decrypt_field_list=None):
        result._dp_pair_data.append(data)

    lcls['result'] = result
    lcls['store'] = store
    lcls['load'] = load
    lcls['private'] = PrivateData
    lcls['user'] = user
    lcls['new_collection'] = new_collection
    lcls['encrypt'] = encrypt
    lcls['return_to_app'] = return_to_app
    lcls['app'] = app_module
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

def execute(user_info, program, app_id=None, purpose=None, app_module=None):
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


    glbls = {'__builtins__': safe_builtins}
    lcls = assemble_locals(result=result,
                           user_specific=users_specific,
                           app_id=app_id,
                           app_module=app_module)
    try:
        c_program = retrieve_compiled(program)
        exec(c_program, glbls, lcls)
    except:
        print(traceback.format_exc())
        json_output = {'result': 'error', 'traceback': traceback.format_exc()}
        return json_output

    json_output['stored_items'] = result._stored_keys
    json_output['encrypted_data'] = result._encrypted_data
    json_output['data'] = result._dp_pair_data
    json_output['result'] = 'ok'
    return json_output
