from ancile_core.policy import Policy
from time import time
from ancile_core.policy_sly import PolicyParser
from ancile_web.errors import PolicyError, AncileException
from ancile_core.datapolicypair import DataPolicyPair
import ancile_core.policy as policy
import ancile_core.time as ancile_web_time
from functools import wraps
from copy import deepcopy
from ancile_core.policy import Policy
import logging
logger = logging.getLogger(__name__)


class Collection(object):
    def __init__(self, data_points=None):
        self._data_points = data_points if data_points else list()
        self._created_at = ancile_web_time.get_timestamp()
        self._previous_access = self._created_at

    def __len__(self):
        return len(self._data_points)

    def __repr__(self):
        return f"<Collection size:{len(self)}. The policy: {self.get_collection_policy()}"

    def get_collection_policy(self):
        rolling_policy = PolicyParser.parse_it("ANYF*")
        for dpp in self._data_points:
            rolling_policy = Policy._simplify(['intersect', rolling_policy, dpp._policy._policy])
        return Policy(rolling_policy)


    def _check_collection_policy(self, command, **kwargs):
        """
        Check that intersection policy allows the command

        :param command:
        :return:
        """
        collection_policy = self.get_collection_policy()
        return collection_policy.check_allowed(command, **kwargs)


    def _advance_collection_policy(self, command, **kwargs):
        """
        Update the policy only if the collection policy allows the update.
        We implement it by computing a collection policy on provided DPPs, and
        advance each DPP only if the collection permits it.

        :param command:
        :return:
        """
        if self._check_collection_policy(command, **kwargs):
            for dpp in self._data_points:
                dpp._advance_policy_error(command, **kwargs)
        else:
            raise PolicyError(f"Collection does not allow the command: {command} with arguments {kwargs}")


    def add_to_collection(self, data: DataPolicyPair):
        """
        Add to collection updates both collection policy and individual policy

        :param data:
        :return:
        """
        command = 'add_to_collection'
        data._advance_policy_error(command)
        self._advance_collection_policy(command)
        self._data_points.append(data)

    def remove_from_collection(self, index, reverse_add=False):
        """

        :param index: position of the object in the collection
        :param reverse_add: if reverse, then recover the policy
            otherwise, just perform a stem on remove_from_collection
        :return:
        """


        dpp = self._data_points.pop(index)
        if reverse_add:
            dpp._policy = Policy._simplify(['concat', ['exec', 'add_to_collection', {}], dpp._policy._policy])
        else:
            command = 'remove_from_collection'
            dpp._advance_policy_error(command)

        return dpp

    def _delete_expired(self):
        self._data_points = [dp for dp in self._data_points
                                if not dp.is_expired]

    def for_each(self, f, *args, in_place=False, **kwargs):
            if in_place:
                self._data_points = [f(*args, data=dp, **kwargs)
                                     for dp in self._data_points]
                return self
            else:
                new_col = Collection()
                new_col._data_points = [f(*args, data=dp, **kwargs)
                                        for dp in self._data_points]
                return new_col


    def filter(self, lambda_function):

        new_data_points = list()

        for dpp in self._data_points:
            if lambda_function(dpp._data):
                logger.info('')
                dpp._advance_policy_error(['exec', 'filter_keep'])
                new_data_points.append(dpp)
            else:
                dpp._advance_policy_error(['exec', 'filter_remove'])
        new_collection = Collection(new_data_points)
        print(f"Reduced size of collection from {len(self._data_points)} to {len(new_data_points)}")

        return new_collection

    def filter_by_next_command(self, command):
        new_data_points = list()

        for dpp in self._data_points:
            peek_next_policy = dpp._policy.d_step('filter_keep')
            if peek_next_policy.d_step(command):
                dpp._advance_policy_error(['exec', 'filter_keep'])
                new_data_points.append(dpp)
            else:
                dpp._advance_policy_error(['exec', 'filter_remove'])
        new_collection = Collection(new_data_points)
        print(f"Reduced size of collection from {len(self._data_points)} to {len(new_data_points)}")

        return new_collection




def reduction_fn(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        collection = kwargs.get('collection', None)
        if not isinstance(collection, Collection):
            raise AncileException('Please provide a Collection object as `collection` argument.')
        policy = collection.get_collection_policy().d_step({'command': f.__name__,
                                                            'kwargs': kwargs})
        if not policy:
            raise PolicyError(f'Collection policy prevented execution of \'{f.__name__}\'')

        kwargs['collection'] = [x._data for x in collection._data_points]
        logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}')
        data = f(*args, **kwargs)
        dp = DataPolicyPair(policy, None, 'reduce', None, None)
        dp._data = data

        return dp

    return wrapper
