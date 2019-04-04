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