from ancile_core.decorators import transform_decorator, aggregate_decorator, comparison_decorator, filter_decorator
from ancile_web.errors import AncileException
from ancile_core.collection import reduction_fn

@transform_decorator
def test(data):
    data['test'] = True
    # print('FUNC: test')
    return True

@transform_decorator
def keep_keys(data, keys):
    dropped = set(data.keys()) - set(keys)
    for key in dropped:
        del data[key] 
    return True

@transform_decorator
def keep_path_keys(data, path, keys):
    dropped = set(data[path].keys()) - set(keys)
    for key in dropped:
        del data[path][key]
    return True

@transform_decorator
def drop_keys(data, keys):
    for key in keys:
        del data[key]
    return True

@transform_decorator
def flatten(data):
    out = flat_dict(data)
    data.clear()
    data.update(out)
    return True

def flat_dict(d):
    out = {}
    for key, val in d.items():
        if isinstance(val, dict):
            deeper = flat_dict(val).items()
            out.update({str(key) + '_' + str(key2): val2 for key2, val2 in deeper})
        else:
            out[key] = val
    return out

@aggregate_decorator()
def basic_aggregation(data):
    return True

@aggregate_decorator(True)
def aggregate_and(data):
    if all(list(map(lambda x: isinstance(x, bool), data['aggregated']))):
        data['aggregate_and'] = all(data.pop('aggregated'))
    else:
        raise AncileException("All values to \"aggregate_and()\" must be booleans")

    return data

@aggregate_decorator(True)
def aggregate_or(data):
    if all(list(map(lambda x: isinstance(x, bool), data['aggregated']))):
        data['aggregate_or'] = any(data.pop('aggregated'))
    else:
        raise AncileException("All values to \"aggregate_and()\" must be booleans")

    return data

@aggregate_decorator(True)
def quorum(data, threshold):
    percentage = sum([int(x) for x in data['aggregated']]) / len(data['aggregated'])
    data['quorum'] = percentage >= threshold

    return data


@comparison_decorator
def field_comparison(data, field_path, comparison_operator, value):
    """

    We use following lib: https://docs.python.org/3.7/library/operator.html
    :param data:
    :param field_path: can take a list that will be a path to the field
    :param comparison_operator: refer to the operators in the wiki
    :param value: value to comparison
    :return:
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


@transform_decorator
def counter(data: dict):
    if data.get('counter', False):
        data['counter'] = 0
    data['counter'] += 1

    return data

@reduction_fn
def collection_average(data: list, results: dict, value_key: str=None):
    if value_key is None:
        raise ValueError("'value_key' must have a value.")

    rolling_value = 0
    for item in data:
        rolling_value += item[value_key]

    results['collection_average'] = rolling_value / len(data)

@reduction_fn
def collection_and(data: list, results: dict, value_key: str=None):
    if value_key is None:
        raise ValueError("'value_key' must have a value.")
    if not all((isinstance(item[value_key], bool) for item in data)):
        raise ValueError("'value_key' must point to a boolean value.")

    results['collection_and'] = all((item[value_key] for item in data))

@reduction_fn
def collection_or(data: list, results: dict, value_key: str=None):
    if value_key is None:
        raise ValueError("'value_key' must have a value.")
    if not all((isinstance(item[value_key], bool) for item in data)):
        raise ValueError("'value_key' must point to a boolean value.")

    results['collection_or'] = any((item[value_key] for item in data))

@reduction_fn
def collection_sum(data: list, results: dict, value_key: str=None):
    if value_key is None:
        raise ValueError("'value_key' must have a value.")

    results['collection_sum'] = sum((item[value_key] for item in data))


@filter_decorator
def no_filter(collection=None):
    print('no_filter')

    return True


def get_token(user):

    return user['token']