from src.micro_data_core_python.decorators import transform_decorator, aggregate_decorator

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

