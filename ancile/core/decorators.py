from core.datapolicypair import DataPolicyPair
from ancile.utils.errors import AncileException
import core.policy as policy
import core.storage as storage
import inspect
from functools import wraps
from core.user_specific import UserSpecific
import logging
from core.collection import Collection
logger = logging.getLogger(__name__)
import copy

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
        new_dp_pair = copy.copy(dp_pair)
        logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}, app: {new_dp_pair._app_id}')
        new_dp_pair._call_transform(f, *args, **kwargs)

        return new_dp_pair

    return wrapper

def external_request_decorator(split_to_collection=False):
    """
    Intended call:
    dp_1 = fetch_data(user_specific=user_specific['user'], data_source='name')
    :param f:
    :return:
    """

    def actual_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            check_args(args)

            user_specific = kwargs.pop('user', False)
            data_source = inspect.getmodule(f).name
            name = kwargs.pop('name', False)
            sample_policy = kwargs.pop('sample_policy', '(ANYF*).return')

            if not isinstance(user_specific, UserSpecific):
                raise ValueError("You have to provide a UserSpecific object to fetch new data.")


            logger.info(f'function: {f.__name__} args: {args}, kwargs: {kwargs}, app: {user_specific}')
            dp_pair = user_specific.get_empty_data_pair(data_source, name=name, sample_policy=sample_policy)
            data = dp_pair._call_external(f, *args, **kwargs)
            dp_pair._data = data
            if not split_to_collection:
                return dp_pair
            else:
                # split data point into collection
                if not isinstance(data, list):
                    raise AncileException('We can only create a collection on list of data')
                data_points = list()
                for entry in data:
                    sub_dp = DataPolicyPair(policy=dp_pair._policy, token=dp_pair._token,
                                            name=dp_pair._name, username=dp_pair._username,
                                            private_data=dp_pair._private_data, app_id=dp_pair._app_id)
                    sub_dp._data = entry
                    sub_dp._advance_policy_error(['exec', 'add_to_collection'])
                    data_points.append(sub_dp)
                logger.info("CREATED A COLLECTION")
                collection = Collection(data_points)
                return collection



        return wrapper
    return actual_decorator


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
                if not (isinstance(dp_pair, DataPolicyPair) or isinstance(dp_pair, Collection)):
                    raise ValueError("You need to provide a Data object. Use get_data to get it.")
                if isinstance(dp_pair, Collection):
                    collection_data = list()
                    for dps in dp_pair._data_points:
                        collection_data.append(dps._data)
                    if reduce:
                        new_data.append(collection_data)
                    else:
                        new_data['collection'] = collection_data
                    continue


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
                from core.user_specific import UserSpecific
                user_specific_dict = kwargs['user_specific']
                new_us = UserSpecific(policies=None, tokens=None, private_data=None,
                                    username='aggregated', app_id=app_id)
                new_us._active_dps['aggregated'] = new_dp
                user_specific_dict['aggregated'] = new_us

            logger.info(f'aggregate function: {f.__name__}. args: {args}, kwargs: {kwargs}, app: {app_id}')
            new_dp._data = new_dp._call(f, *args, scope='aggregate', **kwargs)
            return new_dp
        return wrapper
    return decorator


def filter_decorator(f):
    """
    Still under development and not used yet.

    :param f:
    :return:
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        collection = kwargs.get("collection")
        new_collection = Collection()
        for data_point in collection._data_points:
            value = f(data_point)
            if value:
                data_point._advance_policy('filter_keep')
                new_collection._data_points.append(data_point)
            else:
                data_point._advance_policy('filter_remove')

    return wrapper
