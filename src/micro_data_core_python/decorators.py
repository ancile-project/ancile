from src.micro_data_core_python.datapolicypair import DataPolicyPair


def transform_decorator(f):
    def wrapper(*args, **kwargs):
        print(f'args: {args}')
        print(f'kwargs: {kwargs}')
        if args:
            # let's just ask to specify kwargs. Useful for policy creation.
            raise ValueError("Please specify keyword arguments instead of positions.")

        dp_pair = kwargs.get('data', False)
        if isinstance(dp_pair, DataPolicyPair):
            return dp_pair.call(f, *args, **kwargs)
        else:
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

    return wrapper


def get_data_decorator(f):
    def wrapper(*args, **kwargs):
        print(f'args: {args}')
        print(f'kwargs: {kwargs}')
        if args:
            # let's just ask to specify kwargs. Useful for policy creation.
            raise ValueError("Please specify keyword arguments instead of positions.")
        ds = kwargs.get('data_source', False)
        user_specific = kwargs.get('user_specific', False)
        dp_pair = kwargs.get('data', False)

        if ds and user_specific and isinstance(dp_pair, DataPolicyPair):
            ## COMMENTED OUT FOR THE GEN EMPTY VERSION
            # policy = cls._user_policies[ds]
            # dp_pair = DataPolicyPair(policy)
            # kwargs['data'] = dp_pair
            return user_specific.get_tokens(dp_pair, ds, f, *args, **kwargs)
        else:
            print(f.__name__)
            print(ds)
            print(dp_pair)
            print(user_specific)
            raise ValueError("Please specify parameter: data_source.")

    return wrapper


def return_data_decorator(f):
    def wrapper(*args, **kwargs):
        print(f'args: {args}')
        print(f'kwargs: {kwargs}')
        if args:
            # let's just ask to specify kwargs. Useful for policy creation.
            raise ValueError("Please specify keyword arguments instead of positions.")

        dp_pair = kwargs.get('data', False)
        if isinstance(dp_pair, DataPolicyPair):
            return dp_pair.return_data(f, *args, **kwargs)
        else:
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

    return wrapper
