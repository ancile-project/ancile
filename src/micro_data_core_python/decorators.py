from src.micro_data_core_python.datapolicypair import DataPolicyPair


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
            return dp_pair._call_fetch(f, *args, **kwargs)
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
            new_data[dp_pair._name] = dp_pair._data
            set_users.add(dp_pair._username)
            if new_policy:
                new_policy = ['intersect', dp_pair._policy, new_policy]
            else:
                new_policy = dp_pair._policy
        if len(set_users) != len(dp_pairs):
            raise ValueError("You need to provide a separate data object for each username.")

        new_dp = DataPolicyPair(policy=new_policy, token=None, name='Aggregate', username='Aggregate')
        new_dp._data = {'aggregated': new_data}

        return new_dp._use_method(f, *args, **kwargs)

    return wrapper

