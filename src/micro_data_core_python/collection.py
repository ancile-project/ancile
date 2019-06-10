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

    def _check_policy(self, f, **kwargs):
        if not self._policy.check_allowed(f.__name__, **kwargs):
            raise PolicyError()

    @collection_decorator
    def add_to_collection(self, data):
        now = time()
        elapsed_time = now - self._previous_access

        self._check_policy(self.add_to_collection, elapsed=elapsed_time)
        self._data_points.append(data)
        self._previous_access = now

    def _delete_expired(self):
        self._data_points = [dp for dp in self._data_points
                                if not dp.is_expired]


def reduction_fn(f):
    def wrapper(*args, **kwargs):
        collection = kwargs.get('data', False)

        if isinstance(collection, Collection):
            data_items = []
            rolling_policy = None

            for item in collection._data_times:
                pol = item._policy.d_step()
                if pol:
                    rolling_policy = pol if rolling_policy is None \
                                     else policy.intersect(rolling_policy, pol)
                    data_items.append(item._data)

            kwargs['data'] = data_items
            results = dict()
            kwargs['results'] = results
            value = f(*args, **kwargs)

            dp = DataPolicyPair(rolling_policy, None, 'reduce', None, None)
            dp._data = results
        else:
            raise ValueError("'data' must be a collection object")

        logger.info(f'function: {f.__name__}. args: {args}, kwargs: {kwargs}, app: {dp_pair._app_id}')
        return dp

    return wrapper