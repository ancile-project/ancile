from ancile.utils.errors import PolicyError, AncileException
from ancile.core.primitives.data_policy_pair import DataPolicyPair
import ancile.utils.time as ancile_web_time
from functools import wraps
from ancile.core.primitives.policy import Policy, intersect_list
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
        return f"<Collection size:{len(self)}. The policy: {self.get_collection_policy()}>"

    def get_collection_policy(self):
        """
        Return the policy resulting from the intersection of all policies in
        the collection.

        Note: If there are no points in the collection, it has the ANYF* policy
              otherwise the policy is the intersection of the policies of the
              collected DPPs.

        :return: A Policy object representing the synthesized policy on the
                 collection.
        """
        return intersect_list((dp._policy for dp in self._data_points),
                              empty_policy='ANYF*')


    def _check_collection_policy(self, command, **kwargs) -> bool:
        """
        Check if the collection policy allows the given policy_command.

        :param str command: The name of the policy_command.
        :return: T if the policy_command is allowed, False otherwise
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
            raise PolicyError(f"Collection does not allow the policy_command: {command} with arguments {kwargs}")


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
                dpp._advance_policy_error('filter_keep')
                new_data_points.append(dpp)
            else:
                dpp._advance_policy_error('filter_remove')
        new_collection = Collection(new_data_points)
        print(f"Reduced size of collection from {len(self._data_points)} to {len(new_data_points)}")

        return new_collection

    def filter_by_next_command(self, command):
        new_data_points = list()

        for dpp in self._data_points:
            peek_next_policy = dpp._policy.d_step('filter_keep', None)
            if peek_next_policy.d_step(command, None):
                dpp._advance_policy_error('filter_keep')
                new_data_points.append(dpp)
            else:
                dpp._advance_policy_error('filter_remove')
        new_collection = Collection(new_data_points)
        print(f"Reduced size of collection from {len(self._data_points)} to {len(new_data_points)}")

        return new_collection

