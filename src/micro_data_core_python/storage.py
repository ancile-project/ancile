"""
This is a deprecated sketch of the original storage idea. Will be removed
shortly.
"""
from collections import namedtuple
from datetime import datetime, timedelta
from src.micro_data_core_python.errors import AncileException
import redis
import pickle

Entry = namedtuple("Entry", ['expiry_time', 'namespace', 'data'])
r = redis.Redis(host='localhost', port=6379, db=1)

class DPStore(object):
    def __init__(self, user, app_id, purpose):
        self._dp_dict = dict()
        self._last_access = dict()
        self._redis_key = self.gen_key(user, app_id, purpose)

    def add(self, dp_entry, namespace, expiry_sec):
        entry = self._assemble_entry(dp_entry, namespace, expiry_sec)
        self._insert_and_prune(entry, namespace)

    def add_time_constraint(self, dp_entry, namespace, expiry_sec, 
                            min_time_limit):
        current_time = datetime.utcnow()

        if (self._last_access.get(namespace, None) is not None and 
         (current_time - self._last_access[namespace] < timedelta(seconds=min_time_limit))):
            raise AncileException("Minimum time between stores has not elapsed")
        else:
            self.add(dp_entry, namespace, expiry_sec)
            self._last_access[namespace] = datetime.utcnow()

    @classmethod
    def retrieve(cls, user, app_id, purpose):
        key = DPStore.gen_key(user, app_id, purpose)
        redis_response = r.get(key)
        if redis_response is None:
            return cls(user, app_id, purpose)
        else:
            return pickle.loads(redis_response)

    def _store_DPS(self):
        r.set(self._redis_key, pickle.dumps(self), ex=self._get_timeout())

    def _get_timeout(self):
        current_time = datetime.utcnow()
        max_time = datetime.utcnow()
        print(self._dp_dict)
        for _, item_list in self._dp_dict.items():
            if len(item_list) != 0:
                max_time = max_time if max_time > item_list[-1].expiry_time \
                            else item_list[-1].expiry_time
        time_diff = max_time - current_time
        return time_diff.seconds

    @staticmethod
    def gen_key(user, app_id, purpose):
        return f'{user}.{app_id}.{purpose}.store'
        
    @staticmethod
    def _assemble_entry(dp_entry, namespace, expiry_sec):
        ex_time = datetime.utcnow() + timedelta(seconds=expiry_sec)
        return Entry(ex_time, namespace, dp_entry)

    def _insert_and_prune(self, new_entry, namespace):
        if namespace in self._dp_dict:
            current_time = datetime.utcnow()
            drop_point = None
            insert_index = None
            for index, entry in enumerate(self._dp_dict[namespace]):
                if entry.expiry_time > new_entry.expiry_time:
                    insert_index = index
                    self._dp_dict[namespace].insert(index, new_entry)
                    break
                
                if entry.expiry_time <= current_time:
                    drop_point=index
            if insert_index is None:
                self._dp_dict[namespace].append(new_entry)
            if drop_point is not None:
                del self._dp_dict[namespace][0:drop_point]
        else:
            self._dp_dict[namespace] = [new_entry]


    def return_dps(self, namespace):
        current_time = datetime.utcnow()
        return [x.data for x in self._dp_dict.get(namespace,[]) 
                if x.expiry_time > current_time]
