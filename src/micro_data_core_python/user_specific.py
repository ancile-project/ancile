from src.micro_data_core_python.datapolicypair import DataPolicyPair


class UserSpecific:

    _user_policies = dict()
    _user_tokens = dict()

    def __init__(self, policies, tokens):
        self._user_policies = policies
        self._user_tokens = tokens


    def get_tokens(self, dp_pair, ds, f, *args, **kwargs):
        if self._user_tokens.get(ds, False):
            kwargs['token'] = self._user_tokens[ds]
            return dp_pair.call(f, *args, **kwargs)
        else:
            raise ValueError(f"No tokens {ds} for the user")


    def get_empty_data_pair(self, data_source):
        if self._user_policies.get(data_source, False):
            policy = self._user_policies[data_source]
            return DataPolicyPair(policy)
        else:
            raise ValueError(f"No policies {data_source} for the user")