from ancile_core.policy import Policy
from time import time
from ancile_web.errors import PolicyError, AncileException
from ancile_core.datapolicypair import DataPolicyPair
# from ancile_core.decorators import collection_decorator
import ancile_core.policy as policy
import ancile_core.time as ancile_web_time
from functools import wraps
from copy import deepcopy
from ancile_core.policy import Policy
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
    def __init__(self):
        self._data_points = list()
        self._created_at = ancile_web_time.get_timestamp()
        self._previous_access = self._created_at

    def __len__(self):
        return len(self._data_points)

    def __repr__(self):
        return f"<Collection size:{len(self)}. The policy: {self.get_collection_policy()}"

    def get_collection_policy(self):
        rolling_policy = None
        for dpp in self._data_points:
            if rolling_policy:
                rolling_policy = Policy._simplify(['intersection', rolling_policy, dpp._policy._policy])
            else:
                rolling_policy = dpp._policy._policy

        return Policy(rolling_policy)


    def _check_collection_policy(self, command):
        """
        Check that intersection policy allows the command

        :param command:
        :return:
        """
        collection_policy = self.get_collection_policy()
        if collection_policy.check_allowed(command):
            return True
        else:
            return False


    def _advance_collection_policy(self, command):
        """
        Update the policy only if the collection policy allows the update.
        We implement it by computing a collection policy on provided DPPs, and
        advance each DPP only if the collection permits it.

        :param command:
        :return:
        """
        if self._check_collection_policy(command):
            for dpp in self._data_points:
                dpp._advance_policy_error(command)
        else:
            raise AncileException(f"Collection does not allow the command: {command}")


    @collection_decorator
    def add_to_collection(self, data: DataPolicyPair):
        """
        Add to collection updates both collection policy and individual policy

        :param data:
        :return:
        """
        data._advance_policy_error(self.add_to_collection)
        self._advance_collection_policy(self.add_to_collection)
        self._data_points.append(data)

    @collection_decorator
    def remove_from_collection(self, data):

        for index, dpp in enumerate(self._data_points):
            dpp._policy._policy = ['concat', 'add_to_collection', dpp._policy._policy]
            if dpp == data:
                self._data_points.pop(index)





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
        collection = kwargs.get('data', None)
        if isinstance(collection, Collection):
            return AncileException('Please provide a Collection object as `data` argument.')
        collection._advance_collection_policy({'command': f.__name__,
                                                        'kwargs': kwargs})
        policy = collection.get_collection_policy()
        kwargs['data'] = [x._data for x in collection._data_points]
        logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}')
        f(*args, **kwargs)
        dp = DataPolicyPair(policy, None, 'reduce', None, None)
        dp._data = kwargs['data']

        return dp

    return wrapper
