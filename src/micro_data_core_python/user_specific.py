from src.micro_data_core_python.datapolicypair import DataPolicyPair
from src.micro_data_core_python.errors import AncileException
from src.micro_data_core_python.policy_sly import PolicyParser

import logging
logger = logging.getLogger('primary')

class UserSpecific:

    def __init__(self, policies, tokens, private_data, username=None, app_id=None):
        self._username = username
        self._user_policies = policies
        self._user_tokens = tokens
        self._user_private_data = private_data
        self._active_dps = dict()
        self._app_id = app_id
        logger.debug(f'parsed policies for {self._username}: {self._user_policies}')

    def get_empty_data_pair(self, data_source, name=None, sample_policy='ANYF*.return'):
        if data_source == 'test':
            dp_pair = DataPolicyPair(PolicyParser.parse_it(sample_policy), None, data_source,
                                     self._username, None)
            self._active_dps[data_source] = dp_pair
            return dp_pair
        if self._active_dps.get(data_source, False):
            raise AncileException(f"There already exists a Data Policy pair "
                                  f"for {data_source}. Either call "
                                  f"retrieve_existing_dp_pair() or provide empty UUID")
        if self._user_policies.get(data_source, False):
            policy = self._user_policies[data_source]
            token = self._user_tokens[data_source]['access_token']
            dp_name = name if name else data_source
            dp_pair = DataPolicyPair(policy, token, dp_name, 
                                    self._username, self._user_private_data,
                                    app_id=self._app_id)
            self._active_dps[dp_name] = dp_pair
            return dp_pair
        else:
            raise AncileException(f"No policies for provider {data_source}, for"
                                  f" this user. Please ask the user to add the policy.")


    def retrieve_existing_dp_pair(self, data_source):
        if self._active_dps.get(data_source, False):
            return self._active_dps[data_source]
        else:
            raise AncileException(f"The DP for {data_source} doesn't exist. "
                                  "Create the new one, or provide the correct"
                                  "UUID to retrieve saved state.")
