from src.micro_data_core_python.datapolicypair import DataPolicyPair
from src.micro_data_core_python.collection import Collection
from src.micro_data_core_python.errors import AncileException
import redis
import pickle
from uuid import uuid4
from config import REDIS_CONFIG


r = redis.Redis(**REDIS_CONFIG)


def store(obj):
    if not isinstance(obj, DataPolicyPair) and not isinstance(obj, Collection):
        raise AncileException("Cannot store this object.")

    key = str(uuid4())
    if isinstance(obj, DataPolicyPair):
        r.set(key, pickle.dumps(obj), ex=600)
    else:
        r.set(key, pickle.dumps(obj))
    return key


def load(key):
    value = r.get(key)
    if value is None:
        raise AncileException("Nothing stored under this ID.")
    obj = pickle.loads(value)
    if isinstance(obj, DataPolicyPair):
        obj._was_loaded = True
        obj._load_key = key
    return obj


def del_key(key):
    r.delete(key)