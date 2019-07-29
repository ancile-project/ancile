import wrapt
import logging
import copy
import inspect

from ancile.core.user_secrets import UserSecrets

logger = logging.getLogger(__name__)
from ancile.core.decorators import *


class ExternalDecorator(BaseDecorator):

    def process_call(command, is_collection=False):

        user_specific = command.params.pop('user', False)
        data_source = inspect.getmodule(command.function).name
        name = command.params.pop('name', False)
        sample_policy = command.params.pop('sample_policy', '(ANYF*).return')

        if not isinstance(user_specific, UserSecrets):
            raise ValueError("You have to provide a UserSpecific object to fetch new data.")

        dp_pair = user_specific.get_empty_data_pair(data_source, name=name, sample_policy=sample_policy)
        dp_pair._data = dp_pair._call_external(command)
        if not is_collection:
            return dp_pair
        else:
            # split data point into collection
            if not isinstance(data, list):
                raise AncileException('We can only create a collection on list of data')
            data_points = list()
            for entry in data:
                sub_dp = DataPolicyPair(policy=dp_pair._policy, token=dp_pair._token,
                                        name=dp_pair._name, username=dp_pair._username,
                                        private_data=dp_pair._private_data, app_id=dp_pair._app_id)
                sub_dp._data = entry
                sub_dp._advance_policy_error(['exec', 'add_to_collection'])
                data_points.append(sub_dp)
            logger.info("CREATED A COLLECTION")
            collection = Collection(data_points)
            return collection

        return True



