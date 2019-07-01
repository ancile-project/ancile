from ancile_core.datapolicypair import DataPolicyPair
from ancile_core.collection import Collection
from ancile_web.errors import AncileException
import redis
import pickle
from uuid import uuid4
from config.loader import REDIS_CONFIG
import logging
logger = logging.getLogger(__name__)


r = redis.Redis(**REDIS_CONFIG)


def gen_key():
    return uuid4()

def store(obj, key):
    if not isinstance(obj, DataPolicyPair) and not isinstance(obj, Collection):
        raise AncileException("Cannot store this object.")

    if isinstance(obj, DataPolicyPair):
        r.set(key, pickle.dumps(obj), ex=600)
    else:
        r.set(key, pickle.dumps(obj))

    logger.info(f'Stored object {obj} under id \'{key}\'')

def load(key):
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