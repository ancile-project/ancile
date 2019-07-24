"""
Generic Ancile functions meant to be useful on many different forms of data.
"""
from ancile.core.decorators import (transform_decorator, aggregate_decorator,
                             comparison_decorator, filter_decorator, reduction_decorator)
from ancile.utils.errors import AncileException



# =============================================================================
# External Request Generics
# =============================================================================

# Neither of these is presently functional given changes to how data policy
# pairs are created. If we want to use them they'll need some rehabilitation

# @external_request_decorator()
# def get_data(target_url=None, user=None):
#     """
#     Access data from a specific target url with an empty request body.
#     """
#     data = {'output': []}
#     token = get_token(user)

#     r = requests.get(target_url, headers={'Authorization': "Bearer " + token})

#     if r.status_code == 200:
#         data.update(r.json()) # Need to maintain given dict
#     else:
#         print(r.status_code)
#         raise AncileException("Request error")

#     return data

# @external_request_decorator()
# def full_api(user, body=None, target_url=None):
#     """
#     Access data from a specified target_url wih the given body.
#     """
#     data = {'output': []}
#     token = get_token(user)

#     r = requests.get(target_url, headers={'Authorization': "Bearer " + token},
#                      body=body)

#     if r.status_code == 200:
#         data.update(r.json()) # Need to maintain given dict
#     else:
#         print(r.status_code)
#         raise AncileException("Request error")

#     return data


# =============================================================================
# Toy Functions (good for testing)
# =============================================================================

@transform_decorator
def double(data, key):
    """
    Double the value at the given key.

    :param data: The DataPolicyPair's internal data field.
    :param key: The key whose value will be doubled.
    :return: The data with the field doubled
    """
    data[key] *= 2

@transform_decorator
def counter(data: dict):
    """
    Create or increment a counter.

    :param data: The DataPolicyPair's internal data field.
    :return: The data with the field 'counter' incremented. If it does not exist
             it is created with the value 1.
    """
    if data.get('counter', False):
        data['counter'] = 0
    data['counter'] += 1


# =============================================================================
# Transformation Functions
# =============================================================================

@transform_decorator
def keep_keys(data, keys):
    """
    Remove all keys except those listed from a DataPolicyPair.

    :param data: A DataPolicyPair's data field
    :param keys: A list of keys to be retained.
    :return: The data dictionary with only the listed keys.
    """
    dropped = set(data.keys()) - set(keys)
    for key in dropped:
        del data[key]

@transform_decorator
def keep_path_keys(data, path, keys):
    """
    Remove all keys except those listed from the nested dictionary in a
    DataPolicyPair.

    :param data: A DataPolicyPair's data field.
    :param path: The key for the nested dictionary value.
    :param keys: The keys to retain in the nested dictionary.
    :return: The nested dictionary with only the listed keys
    """
    dropped = set(data[path].keys()) - set(keys)
    for key in dropped:
        del data[path][key]

@transform_decorator
def drop_keys(data, keys):
    """
    Delete the given keys from a DataPolicyPair.

    :param data: A DataPolicyPair's data field.
    :param keys: The keys to be deleted.
    :return: The data without the listed field.
    """
    for key in keys:
        if key in data.keys():
            del data[key]

@transform_decorator
def flatten(data):
    """
    Flatten the internal structure of a DataPolicyPair.

    :param data: A DataPolicyPair's internal data field.
    :return: The DataPolicyPair's data in a flattened format.
    """
    out = flat_dict(data)
    data.clear()
    data.update(out)

def flat_dict(d):
    """
    Flatten the input dictionary.

    :param dict d: The dictionary to be flattened
    :return: the dictionary with of the form 'key_subkey_subsubkey ... '
    :rtype: dict
    """
    out = {}
    for key, val in d.items():
        if isinstance(val, dict):
            deeper = flat_dict(val).items()
            out.update({str(key) + '_' + str(key2): val2 for key2, val2 in deeper})
        else:
            out[key] = val
    return out


# =============================================================================
# Aggregation Functions
# =============================================================================

@aggregate_decorator()
def basic_aggregation(data):
    """Aggregate two DataPolicyPairs together without changing the data."""
    pass

@aggregate_decorator(reduce=True)
def aggregate_and(data):
    """
    Produce an aggregate value with the AND of the specified boolean fields
    for each input object.

    Note, this depends on the VALUE_KEYS parameter used by the decorator.

    :param data: A list of boolean values
    :return: The AND of the list values
    """
    if all(list(map(lambda x: isinstance(x, bool), data['aggregated']))):
        data['aggregate_and'] = all(data.pop('aggregated'))
    else:
        raise AncileException("All values to \"aggregate_and()\" must be booleans")

    return data

@aggregate_decorator(reduce=True)
def aggregate_or(data):
    """
    Produce an aggregate value with the OR of the specified boolean fields
    for each input object.

    Note, this depends on the VALUE_KEYS parameter used by the decorator.

    :param data: A list of boolean values
    :return: The OR of the list values
    """
    if all(list(map(lambda x: isinstance(x, bool), data['aggregated']))):
        data['aggregate_or'] = any(data.pop('aggregated'))
    else:
        raise AncileException("All values to \"aggregate_and()\" must be booleans")

    return data

@aggregate_decorator(reduce=True)
def quorum(data, threshold):
    """
    Determine if the percentage of boolean values in the given list greater than
    or equal to the given threshold percentage.

    Note: this depends on the VALUE_KEYS parameter used by the decorator.

    :param data: A list of boolean values based on the DataPolicyPair inputs
    :param threshold: A float between 0 and 1 representing the percentage of
                      group required.
    :return: T if the quorum has been met and false otherwise.
    """
    percentage = sum([int(x) for x in data['aggregated']]) / len(data['aggregated'])
    data['quorum'] = percentage >= threshold

    return data


# =============================================================================
# Comparison Functions
# =============================================================================

@comparison_decorator
def field_comparison(data, field_path, comparison_operator, value):
    """
    A generic comparison operator that compares a given key in the DataPolicyPair
    to the given value with the comparison operator.

    :param data: The DataPolicyPair's internal data field
    :param field_path: The key value to be compared. Can either be a string or
                       a list in the case of nested dictionaries.
    :param comparison_operator: One of 'lt', 'le', 'eq', 'ge', 'gt'. The comparison
                                to execute between the given key/value and the
                                given value.
    :return: The boolean result of the comparison. Used by the decorator to
             advance the policy.
    """
    import operator

    attr_getter = operator.attrgetter(comparison_operator)
    comparison = attr_getter(operator)
    data_value = data
    if isinstance(field_path, list):
        for i in field_path:
            data_value = data_value[i]
    else:
        data_value = data_value[field_path]

    data['output'].append(
        f"Comparing {data_value} from {field_path} with {value} using operator {comparison_operator}")

    return comparison(data_value, value)


# =============================================================================
#  Reduction Functions
# =============================================================================

@reduction_decorator
def collection_average(collection: list, value_key: str=None):
    """
    Compute the average value of a given field across a collection.

    :param list collection: The list of DataPolicyPair data fields.
    :param str value_key: The key value to be averaged across.
    :return: The average value at the given key.
    """
    if value_key is None:
        raise ValueError("'value_key' must have a value.")

    rolling_value = 0
    for item in collection:
        rolling_value += item[value_key]

    return {'collection_average': rolling_value / len(collection)}

@reduction_decorator
def collection_and(collection: list, value_key: str=None):
    """
    Compute the boolean AND of a given field across a collection.

    :param list collection: The list of DataPolicyPair data fields.
    :param str value_key: The key to be operated on.
    :return: The boolean AND of the values at the key in each element of the
             collection.
    """
    if value_key is None:
        raise ValueError("'value_key' must have a value.")
    if not all((isinstance(item[value_key], bool) for item in collection)):
        raise ValueError("'value_key' must point to a boolean value.")

    return {'collection_and':all((item[value_key] for item in collection))}

@reduction_decorator
def collection_or(collection: list, value_key: str=None):
    """
    Compute the boolean OR of a given field across a collection.

    :param list collection: The list of DataPolicyPair data fields.
    :param str value_key: The key to be operated on.
    :return: The boolean OR of the values at the key in each element of the
             collection.
    """
    if value_key is None:
        raise ValueError("'value_key' must have a value.")
    if not all((isinstance(item[value_key], bool) for item in collection)):
        raise ValueError("'value_key' must point to a boolean value.")

    return {'collection_or': any((item[value_key] for item in collection))}

@reduction_decorator
def collection_sum(collection: list, value_key: str=None):
    """
    Compute the sum value of a given field across a collection.

    :param list collection: The list of DataPolicyPair data fields.
    :param str value_key: The key to be operated on.
    :return: The sum of all values at the given key in each element of the
             collection.
    """
    if value_key is None:
        raise ValueError("'value_key' must have a value.")

    return {'collection_sum': sum((item[value_key] for item in collection))}

@filter_decorator
def no_filter(collection=None):
    print('no_filter')

    return True

def get_token(user):
    return user['token']