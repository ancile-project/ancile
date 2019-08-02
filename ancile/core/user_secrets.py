from ancile.core.primitives.data_policy_pair import DataPolicyPair
from ancile.utils.errors import AncileException
from ancile.core.primitives.policy_helpers.policy_parser import PolicyParser

import logging
logger = logging.getLogger(__name__)


class UserSecrets:

    def __init__(self, policies, tokens, private_data, username=None, app_id=None):
        self._username = username
        self._user_policies = policies
        self._user_tokens = tokens
        self._user_private_data = private_data
        self._active_dps = dict()
        self._app_id = app_id
        logger.debug(f'parsed policies for {self._username}: {self._user_policies}')

    def __repr__(self):
        return f"<{self._username}>"

    def get_empty_data_pair(self, data_source, name=None, sample_policy='ANYF*.return'):
        """
        Returns a new Data Policy Pair object that has no data.

        :param data_source:
        :param name:
        :param sample_policy:
        :return:
        """

        if data_source == 'test':
            dp_pair = DataPolicyPair(PolicyParser.parse_it(sample_policy), None, data_source,
                                     self._username, None)
            self._active_dps[data_source] = dp_pair
            return dp_pair
        if self._user_policies.get(data_source, False):
            policy = self._user_policies[data_source]
            token = self._user_tokens[data_source]
            dp_name = name if name else data_source
            dp_pair = DataPolicyPair(policy, token, dp_name, 
                                    self._username, self._user_private_data,
                                    app_id=self._app_id)
            self._active_dps[dp_name] = dp_pair
            return dp_pair
        else:
            raise AncileException(f"No policies for provider {data_source}, for"
                                  f" this user. Please ask the user to add the policy.")
