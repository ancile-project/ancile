from ancile_core.policy import Policy
from time import time
from ancile_web.errors import PolicyError
from ancile_core.datapolicypair import DataPolicyPair
# from ancile_core.decorators import collection_decorator
import ancile_core.policy as policy
import ancile_core.time as ancile_web_time
from functools import wraps
from copy import deepcopy

import logging
logger = logging.getLogger(__name__)


def collection_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        dp_pair = kwargs.get('data', False)
        if not isinstance(dp_pair, DataPolicyPair):
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

        logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}, app: {dp_pair._app_id}')
        return dp_pair._call_collection(f, *args, **kwargs)

    return wrapper


class Collection(object):
    def __init__(self, initial_policy='ANYF*'):
        self._policy = Policy(initial_policy)
        self._data_points = list()
        self._created_at = ancile_web_time.get_timestamp()
        self._previous_access = self._created_at

    def __len__(self):
        return len(self._data_points)

    def _check_policy(self, f, **kwargs):
        if not self._policy.check_allowed(f.__name__, kwargs):
            raise PolicyError()

    def __repr__(self):
        return f"<Collection size:{len(self)}"

    @collection_decorator
    def add_to_collection(self, data):
        now = ancile_web_time.get_timestamp()
        elapsed_time = ancile_web_time.seconds_elapsed(self._previous_access, now)

        self._check_policy(self.add_to_collection, elapsed=elapsed_time)
        self._data_points.append(data)
        self._previous_access = now

    def _delete_expired(self):
        self._data_points = [dp for dp in self._data_points
                                if not dp.is_expired]

    def for_each(self, f, *args, in_place=False, **kwargs):
        new_policy = self._policy.d_step({'command':f.__name__,
                                          'kwargs': kwargs})
        if new_policy:
            if in_place:
                self._policy = new_policy
                if self._policy:
                    for dp in self._data_points:
                        dp._call_transform(f, *args, **kwargs)
                return self
            else:
                new_col = Collection(new_policy)
                new_col._data_points = deepcopy(self._data_points)
                for dp in new_col._data_points:
                    f(*args, data=dp, **kwargs)
                return new_col
        else:
            raise PolicyError()


def reduction_fn(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        collection = kwargs.get('data', False)
        filter_flag = kwargs.pop('filter', True)

        if isinstance(collection, Collection):
            data_items = []
            rolling_policy = collection._policy.d_step({'command': f.__name__,
                                                        'kwargs': kwargs})
            if not rolling_policy:
                raise PolicyError()

            for item in collection._data_points:
                pol = item._policy.d_step({'command': f.__name__,
                                           'kwargs': kwargs})
                if pol:
                    rolling_policy = policy.intersect(rolling_policy, pol)
                    data_items.append(item._data)
                elif not filter_flag:
                    raise PolicyError

            kwargs['data'] = data_items
            dp = DataPolicyPair(rolling_policy, None, 'reduce', None, None)

            kwargs['results'] = dp._data
            f(*args, **kwargs)

        else:
            raise ValueError("'data' must be a collection object")

        logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}')
        return dp

    return wrapper
