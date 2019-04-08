from src.micro_data_core_python.decorators import transform_decorator, aggregate_decorator, reduce_aggregate_decorator
from src.micro_data_core_python.errors import AncileException

@transform_decorator
def test(data):
    data['test'] = True
    print('FUNC: test')
    return True

@transform_decorator
def filter_floor(floor):
    print("FUNC: filter_floor" + str(floor))
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

@aggregate_decorator
def basic_aggregation(data):
    print(data)
    return True

@reduce_aggregate_decorator
def aggregate_and(data):
    if all(list(map(lambda x: isinstance(x, bool), data['aggregated']))):
        data['aggregate_and'] = all(data.pop('aggregated'))
    else:
        raise AncileException("All values to \"aggregate_and()\" must be booleans")

@reduce_aggregate_decorator
def aggregate_or(data):
    if all(list(map(lambda x: isinstance(x, bool), data['aggregated']))):
        data['aggregate_and'] = any(data.pop('aggregated'))
    else:
        raise AncileException("All values to \"aggregate_and()\" must be booleans")


@transform_decorator
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

    if comparison(data_value, value):
        return True
    else:
        error = f"The value {data_value} couldn't be compared with {value} using operator {comparison_operator}"
        raise AncileException(error)
