from ancile.core.user_secrets import UserSecrets
from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.core.primitives.policy_helpers.private_data import PrivateData
from ancile.core.primitives.collection import Collection
import pprint
from config.loader import configs
from ancile.core.decorators import TransformDecorator
import types


def gen_module_namespace():
    import pkgutil
    import importlib
    import ancile.lib as base
    from ancile.lib._config import exclude

    importlib.invalidate_caches()

    prefix_name = base.__name__ + '.'

    module_namespace = dict()

    for _, mod_name, is_pac in pkgutil.iter_modules(path=base.__path__):
        if not is_pac and mod_name not in exclude:
            module_namespace[mod_name] = importlib.import_module(prefix_name + mod_name)

    for library in configs.get('libraries', []):
        module = importlib.import_module(library)
        for k, v in vars(module).items():
            if isinstance(v, types.FunctionType):
                decorator = TransformDecorator()
                vars(module)[k] = decorator(v)
        module_namespace[library] = module

    return module_namespace


# we only need to do this once per deployment.
module_namespace = gen_module_namespace()


def assemble_locals(storage, result, users_secrets, app_id, app_module=None, data_points=None):
    lcls = module_namespace

    def user(name: str) -> UserSecrets:
        return users_secrets[name]

    def store(obj, name):
        key = storage.gen_key()
        storage._store(obj, f'{app_id}:{key}')
        result._stored_keys[name] = key
        if isinstance(obj, DataPolicyPair) and obj._was_loaded:
            storage.del_key(obj._load_key)

    def encrypt(obj, name):
        key = storage.gen_key()
        encrypted_data = encrypt(obj, f'{app_id}:{key}')
        result._stored_keys[name] = key
        result._encrypted_data[name] = encrypted_data

    def new_collection():
        return Collection()

    def load(key):
        return storage._load(f'{app_id}:{key}')

    def sample_dpp(data, policy):
        dpp = DataPolicyPair(policy=policy, name='test', token=None, username='test', private_data=None)
        dpp._data = data
        return dpp

    lcls['result'] = result
    lcls['store'] = store
    lcls['load'] = load
    lcls['private'] = PrivateData
    lcls['user'] = user
    lcls['new_collection'] = new_collection
    lcls['encrypt'] = encrypt
    lcls['return_to_app'] = result.return_to_app
    lcls['app'] = app_module
    lcls['data_points'] = data_points

    if configs['SERVER_DEBUG']:
        # allow printing in the debug state
        lcls['pprint'] = pprint.pprint
        lcls['sample_dpp'] = sample_dpp

    return lcls
