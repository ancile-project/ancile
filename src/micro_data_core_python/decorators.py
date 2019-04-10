from src.micro_data_core_python.datapolicypair import DataPolicyPair
from src.micro_data_core_python.errors import AncileException

def transform_decorator(f):
    def wrapper(*args, **kwargs):
        print(f'function: {f.__name__}. args: {args}, kwargs: {kwargs}')
        if args:
            # let's just ask to specify kwargs. Useful for policy creation.
            raise ValueError("Please specify keyword arguments instead of positions.")
        dp_pair = kwargs.get('data', False)

        if isinstance(dp_pair, DataPolicyPair):
            return dp_pair._call_transform(f, *args, **kwargs)
        else:
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

    return wrapper


def external_request_decorator(f):
    def wrapper(*args, **kwargs):
        print(f'function: {f.__name__}. args: {args}, kwargs: {kwargs}')
        if args:
            # let's just ask to specify kwargs. Useful for policy creation.
            raise ValueError("Please specify keyword arguments instead of positions.")
        dp_pair = kwargs.get('data', False)

        if isinstance(dp_pair, DataPolicyPair):
            return dp_pair._call_external(f, *args, **kwargs)
        else:
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

    return wrapper


def use_type_decorator(f):
    def wrapper(*args, **kwargs):
        print(f'USE function: {f.__name__}. args: {args}, kwargs: {kwargs}')

        dp_pair = kwargs.get('data', False)
        if isinstance(dp_pair, DataPolicyPair):
            return dp_pair._use_method(f, *args, **kwargs)
        else:
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

    return wrapper


def aggregate_decorator(f):
    def wrapper(*args, **kwargs):
        new_data = dict()
        new_policy = None
        dp_pairs = kwargs.get('data', False)
        set_users = set()
        for dp_pair in dp_pairs:
            if not isinstance(dp_pair, DataPolicyPair):
                raise ValueError("You need to provide a Data object. Use get_data to get it.")
            new_data[f'{dp_pair._username}.{dp_pair._name}'] = dp_pair._data
            set_users.add(dp_pair._username)
            if new_policy:
                new_policy = ['intersect', dp_pair._policy, new_policy]
            else:
                new_policy = dp_pair._policy
        # If we're aggregating multiple data pieces from the 
        # same user this won't do the right thing
        # if len(set_users) != len(dp_pairs):
        #     raise ValueError("You need to provide a separate data \
        #                         object for each username.")

        new_dp = DataPolicyPair(policy=new_policy, token=None, 
                                name='Aggregate', username='Aggregate',
                                private_data=dict())
        new_dp._data['aggregated'] = new_data
        if kwargs.get('user_specific', False):
            from src.micro_data_core_python.user_specific import UserSpecific
            user_specific_dict = kwargs['user_specific']
            new_us = UserSpecific(policies=None, tokens=None, private_data=None, username='aggregated')
            new_us._active_dps['aggregated'] = new_dp
            user_specific_dict['aggregated'] = new_us

        new_dp._call_transform(f, *args, scope='aggregate', **kwargs)
        return new_dp

    return wrapper

def reduce_aggregate_decorator(f):
    def wrapper(*args, **kwargs):
        new_policy = None
        dp_pairs = kwargs.get('data', False)
        if 'value_keys' not in kwargs:
            raise AncileException(f"Missing parameter 'value_keys' for {f.__name__}")
        keys = kwargs.pop('value_keys')

        if isinstance(keys, str):
            keys = [keys] * len(dp_pairs)
        
        if len(keys) != len(dp_pairs):
            raise AncileException("value_keys must either be a single value or a list of the same length as data")

        data_list = []
        for dp_pair,key in zip(dp_pairs, keys):
            if not isinstance(dp_pair, DataPolicyPair):
                raise ValueError("You need to provide a Data object. Use get_data to get it.")
            data_list.append(dp_pair._data[key])

            if new_policy:
                new_policy = ['intersect', dp_pair._policy, new_policy]
            else:
                new_policy = dp_pair._policy

        new_dp = DataPolicyPair(policy=new_policy, token=None,
                                name='Aggregate', username='Aggregate',
                                private_data=dict())
        new_dp._data['aggregated'] = data_list

        new_dp._call_transform(f, *args, scope='aggregate', **kwargs)
        return new_dp

    return wrapper