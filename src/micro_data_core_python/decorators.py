from src.micro_data_core_python.datapolicypair import DataPolicyPair


def transform_decorator(f):
    def wrapper(*args, **kwargs):
        print(f'function: {f.__name__}. args: {args}, kwargs: {kwargs}')
        if args:
            # let's just ask to specify kwargs. Useful for policy creation.
            raise ValueError("Please specify keyword arguments instead of positions.")
        dp_pair = kwargs.get('data', False)

        if isinstance(dp_pair, DataPolicyPair):
            return dp_pair.call_transform(f, *args, **kwargs)
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
            return dp_pair.call_fetch(f, *args, **kwargs)
        else:
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

    return wrapper


def return_data_decorator(f):
    def wrapper(*args, **kwargs):
        print(f'function: {f.__name__}. args: {args}, kwargs: {kwargs}')
        if args:
            # let's just ask to specify kwargs. Useful for policy creation.
            raise ValueError("Please specify keyword arguments instead of positions.")

        dp_pair = kwargs.get('data', False)
        if isinstance(dp_pair, DataPolicyPair):
            return dp_pair.return_data(f, *args, **kwargs)
        else:
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

    return wrapper
