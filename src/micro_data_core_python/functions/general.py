from src.micro_data_core_python.decorators import transform_decorator

@transform_decorator
def asdf(data):
    data['asdf'] = True
    print('FUNC: asdf')
    return True

@transform_decorator
def qwer(data):
    data['qwer'] = True
    print('FUNC: qwer')
    return True

@transform_decorator
def zxcv(data):
    data['qwer'] = True
    print('FUNC: zxcv')
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
