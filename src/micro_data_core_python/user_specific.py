from src.micro_data_core_python.datapolicypair import DataPolicyPair


class UserSpecific:

    _user_policies = dict()
    _user_tokens = dict()

    @classmethod
    def transform_decorator(cls, f):
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

    @classmethod
    def get_data_decorator(cls, f):
        def wrapper(*args, **kwargs):
            print(f'args: {args}')
            print(f'kwargs: {kwargs}')
            if args:
                # let's just ask to specify kwargs. Useful for policy creation.
                raise ValueError("Please specify keyword arguments instead of positions.")
            ds = kwargs.get('data_source', False)
            dp_pair = kwargs.get('data', False)

            if ds:
                ## COMMENTED OUT FOR THE GEN EMPTY VERSION
                # policy = cls._user_policies[ds]
                # dp_pair = DataPolicyPair(policy)
                # kwargs['data'] = dp_pair
                kwargs['token'] = cls._user_tokens.get(ds, None)
                dp_pair.call(f, *args, **kwargs)
            else:
                raise ValueError("Please specify parameter: data_source.")

        return wrapper

    @classmethod
    def return_data_decorator(cls, f):
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
