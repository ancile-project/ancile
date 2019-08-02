from ancile.core.decorators import *
import logging

from ancile.core.primitives import *
from ancile.core.user_secrets import UserSecrets
from ancile.utils.errors import AncileException


logger = logging.getLogger(__name__)


class AggregateDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False, reduce=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('aggregate')
        self.reduce = reduce

    def process_call(self, command):
        logger.debug(f'Calling Aggregate "{command.function_name}"')

        new_data = dict() if not self.reduce else list()
        new_policy = None
        dp_pairs = command.params.get('data', [])
        set_users = set()
        app_id = None

        keys = command.params.pop('value_keys', None)
        if self.reduce:
            if isinstance(keys, str):
                keys = [keys] * len(dp_pairs)

            if len(keys) != len(dp_pairs):
                raise AncileException("value_keys must either be a single value or a list of the same length as data")

        for index, dp_pair in enumerate(dp_pairs):
            if not (isinstance(dp_pair, DataPolicyPair) or isinstance(dp_pair, Collection)):
                raise ValueError("You need to provide a Data object. Use get_data to get it.")
            if isinstance(dp_pair, Collection):
                collection_data = list()
                for dps in dp_pair._data_points:
                    collection_data.append(dps._data)
                if self.reduce:
                    new_data.append(collection_data)
                else:
                    new_data['collection'] = collection_data
                continue

            app_id = dp_pair._app_id if app_id is None else app_id

            if self.reduce:
                new_data.append(dp_pair._data[keys[index]])
            else:
                new_data[f'{dp_pair._username}.{dp_pair._name}'] = dp_pair._data

            set_users.add(dp_pair._username)
            if new_policy is None:
                new_policy = Policy(dp_pair._policy)
            else:
                new_policy = new_policy.intersect(dp_pair._policy)

        new_dp = DataPolicyPair(policy=new_policy, token=None,
                                name='Aggregate', username='Aggregate',
                                private_data=dict(), app_id=app_id)
        new_dp._data['aggregated'] = new_data
        if command.params.get('user_specific', False):
            user_specific_dict = command.params['user_specific']
            new_us = UserSecrets(policies=None, tokens=None, private_data=None,
                                 username='aggregated', app_id=app_id)
            new_us._active_dps['aggregated'] = new_dp
            user_specific_dict['aggregated'] = new_us

        logger.info(f'aggregate function: {command}, app: {app_id}')
        new_dp._data = new_dp._call_transform(command)

        return new_dp
