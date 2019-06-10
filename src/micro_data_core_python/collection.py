from src.micro_data_core_python.policy import Policy
from time import time
from src.micro_data_core_python.errors import PolicyError
from src.micro_data_core_python.datapolicypair import DataPolicyPair
from src.micro_data_core_python.decorators import collection_decorator
import src.micro_data_core_python.policy as policy

import logging
logger = logging.getLogger('api')


class Collection(object):
    def __init__(self, initial_policy='ANYF*'):
        self._policy = Policy(initial_policy)
        self._data_points = list()
        self._previous_access = 0

    def __len__(self):
        return len(self._data_points)

    def _check_policy(self, fname, **kwargs):
        if not self._policy.check_allowed(fname, kwargs):
            raise PolicyError()

    @collection_decorator
    def add_to_collection(self, data):
        now = time()
        elapsed_time = now - self._previous_access

        self._check_policy('add_to_collection', elapsed=elapsed_time)
        self._data_points.append(data)
        self._previous_access = now

    def _delete_expired(self):
        self._data_points = [dp for dp in self._data_points
                                if not dp.is_expired]


def reduction_fn(f):
    def wrapper(*args, **kwargs):
        collection = kwargs.get('data', False)
        filter_flag = kwargs.pop('filter', True)

        if isinstance(collection, Collection):
            collection._check_policy(f.__name__, **kwargs)

            data_items = []
            rolling_policy = None

            for item in collection._data_points:
                pol = item._policy.d_step({'command': f.__name__, 'kwargs': kwargs})
                if pol:
                    rolling_policy = pol if rolling_policy is None \
                                     else policy.intersect(rolling_policy, pol)
                    data_items.append(item._data)
                elif not filter_flag:
                    raise PolicyError

            kwargs['data'] = data_items
            dp = DataPolicyPair(rolling_policy, None, 'reduce', None, None)

            kwargs['results'] = dp._data
            f(*args, **kwargs)

        else:
            raise ValueError("'data' must be a collection object")

        logger.info(f'function: {f.__name__}. args: {args}, kwargs: {kwargs}')
        return dp

    return wrapper