from src.micro_data_core_python.datapolicypair import DataPolicyPair
from src.micro_data_core_python.collection import Collection
from src.micro_data_core_python.errors import AncileException
import redis
import pickle
from uuid import uuid4
from src.secret import REDIS_CONFIG


r = redis.Redis(**REDIS_CONFIG)


def store(obj):
    if not isinstance(obj, DataPolicyPair) and not isinstance(obj, Collection):
        raise AncileException("Cannot store this object.")

    key = str(uuid4())
    r.set(key, pickle.dumps(obj))
    return key


def load(key):
    value = r.get(key)
    if not key:
        raise AncileException("Nothing stored under this ID.")
    obj = pickle.loads(value)
    return obj

