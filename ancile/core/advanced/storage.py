from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.core.primitives.collection import Collection
from ancile.utils.errors import AncileException
import redis
import pickle
from uuid import uuid4
from config.loader import REDIS_CONFIG
from ancile.core.advanced.encryption import encrypt
import logging
logger = logging.getLogger(__name__)


r = redis.Redis(**REDIS_CONFIG)


def gen_key():
    return uuid4()

def _store_encrypted(obj, key):
    if not isinstance(obj, DataPolicyPair):
        raise AncileException('Encrypted storage only applies to DataPolicyPairs')

    keys, crypt = encrypt(obj._data)
    obj._data.clear()
    obj._encryption_keys.update(**keys)

    r.set(key, pickle.dumps(obj))
    logger.info(f'Stored encrypted object {obj} under id \'{key}\'')
    return crypt


def _store(obj, key):
    if not isinstance(obj, DataPolicyPair) and not isinstance(obj, Collection):
        raise AncileException("Cannot store this object.")

    if isinstance(obj, DataPolicyPair):
        r.set(key, pickle.dumps(obj), ex=600)
    else:
        r.set(key, pickle.dumps(obj))

    logger.info(f'Stored object {obj} under id \'{key}\'')

def _load(key):
    value = r.get(key)
    if value is None:
        raise AncileException("Nothing stored under this ID.")
    obj = pickle.loads(value)
    if isinstance(obj, DataPolicyPair):
        obj._was_loaded = True
        obj._load_key = key

    logger.info(f'Loaded object {obj} from id \'{key}\'')
    return obj


def del_key(key):
    r.delete(key)