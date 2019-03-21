from src.micro_data_core_python.datapolicypair import DataPolicyPair
from src.micro_data_core_python.functions import use_type

class UserSpecific:

    _user_policies = dict()
    _user_tokens = dict()

    def __init__(self, policies, tokens, result_field):
        self._user_policies = policies
        self._user_tokens = tokens
        self._result = result_field


    def get_empty_data_pair(self, data_source):
        if self._user_policies.get(data_source, False):
            policy = self._user_policies[data_source]
            token = self._user_tokens[data_source]['access_token']
            return DataPolicyPair(policy, token)
        else:
            raise ValueError(f"No policies {data_source} for the user")
    
    def return_data(self, dp):
        self._result = use_type.return_data(data=dp)