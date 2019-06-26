from ancile_core.datapolicypair import DataPolicyPair
from ancile_web.errors import AncileException
import ancile_core.policy as policy
import ancile_core.storage as storage
import inspect
from functools import wraps
from ancile_core.user_specific import UserSpecific
import logging
from ancile_core.collection import Collection
logger = logging.getLogger(__name__)

def check_args(args):
    if args:
        raise ValueError("Please specify keyword arguments instead of positions.")

def check_data(dp_pair):
    if not isinstance(dp_pair, DataPolicyPair):
        raise ValueError("You need to provide a Data object. Use get_data to get it.")

def decorator_preamble(args, kwargs) -> DataPolicyPair:
    check_args(args)
    dp_pair = kwargs.get('data', False)
    check_data(dp_pair)
    return dp_pair


def transform_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        dp_pair = decorator_preamble(args, kwargs)

        logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}, app: {dp_pair._app_id}')
        dp_pair._call_transform(f, *args, **kwargs)
        return True

    return wrapper


def store_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        dp_pair = decorator_preamble(args, kwargs)

        logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}, app: {dp_pair._app_id}')
        return dp_pair._call_store(f, *args, **kwargs)

    return wrapper

def external_request_decorator(f):
    """
    Intended call:
    dp_1 = fetch_data(user_specific=user_specific['user'], data_source='name')
    :param f:
    :return:
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        check_args(args)

        user_specific = kwargs.pop('user', False)
        data_source = inspect.getmodule(f).name
        name = kwargs.pop('name', False)
        sample_policy = kwargs.pop('sample_policy', '(ANYF*).return')

        if isinstance(user_specific, UserSpecific):
            logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}, app: {user_specific}')
            dp_pair = user_specific.get_empty_data_pair(data_source, name=name, sample_policy=sample_policy)
            dp_pair._call_external(f, *args, **kwargs)
            return dp_pair
        else:
            raise ValueError("You have to provide a UserSpecific object to fetch new data.")

    return wrapper


def use_type_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        dp_pair = kwargs.get('data', False)
        check_data(dp_pair)

        logger.info(f'USE function: {f.__name__} args: {args}, kwargs: {kwargs}, app: {dp_pair._app_id}')
        ret = dp_pair._use_method(f, *args, **kwargs)
        if dp_pair._was_loaded:
            storage.del_key(dp_pair._load_key)
        return ret

    return wrapper


def comparison_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        dp_pair = decorator_preamble(args, kwargs)

        dependent = kwargs.pop('dependent_dp', False)

        if isinstance(dependent, DataPolicyPair):
            dp_pair._resolve_private_data_keys(kwargs)
            dependent._advance_policy_error('dependent_comparison', **kwargs,
                                            **dp_pair.metadata)
            dp_pair._advance_policy_error(f.__name__, **kwargs,
                                          **dependent.metadata)
            dp_pair._resolve_private_data_values(kwargs)

            kwargs['data'] = dependent._data
            result = f(*args, **kwargs)
            dp_pair._advance_policy_error("_enforce_comparison",
                                          result=result)
        else:
            logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}, app: {dp_pair._app_id}')
            result = dp_pair._call_transform(f, *args, **kwargs)
            dp_pair._advance_policy_error("_enforce_comparison",
                                          result=result)

        return result

    return wrapper


def aggregate_decorator(reduce=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            new_data = dict() if not reduce else list()
            new_policy = None
            dp_pairs = kwargs.get('data', [])
            set_users = set()
            app_id = None

            keys = kwargs.pop('value_keys', None)
            if reduce:
                if isinstance(keys, str):
                    keys = [keys] * len(dp_pairs)

                if len(keys) != len(dp_pairs):
                    raise AncileException("value_keys must either be a single value or a list of the same length as data")

            for index, dp_pair in enumerate(dp_pairs):
                if not isinstance(dp_pair, DataPolicyPair):
                    raise ValueError("You need to provide a Data object. Use get_data to get it.")

                app_id = dp_pair._app_id if app_id is None else app_id

                if reduce:
                    new_data.append(dp_pair._data[keys[index]])
                else:
                    new_data[f'{dp_pair._username}.{dp_pair._name}'] = dp_pair._data

                set_users.add(dp_pair._username)
                if new_policy:
                    new_policy = policy.intersect(dp_pair._policy, new_policy)
                else:
                    new_policy = dp_pair._policy

            new_dp = DataPolicyPair(policy=new_policy, token=None,
                                    name='Aggregate', username='Aggregate',
                                    private_data=dict(), app_id=app_id)
            new_dp._data['aggregated'] = new_data
            if kwargs.get('user_specific', False):
                from ancile_core.user_specific import UserSpecific
                user_specific_dict = kwargs['user_specific']
                new_us = UserSpecific(policies=None, tokens=None, private_data=None,
                                    username='aggregated', app_id=app_id)
                new_us._active_dps['aggregated'] = new_dp
                user_specific_dict['aggregated'] = new_us

            logger.info(f'aggregate function: {f.__name__}. args: {args}, kwargs: {kwargs}, app: {app_id}')
            new_dp._call(f, *args, scope='aggregate', **kwargs)
            return new_dp
        return wrapper
    return decorator


def filter_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        collection = kwargs.get("collection")
        new_collection = Collection()
        for data_point in collection._data_points:
            value = f(data_point)
            if value:
                data_point._policy.check_allowed('filter_keep')
                new_collection._data_points.append(data_point)
            else:
                data_point._policy.check_allowed('filter_remove')

    return wrapper
