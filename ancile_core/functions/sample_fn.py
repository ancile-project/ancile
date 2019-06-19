from ancile_core.decorators import transform_decorator, external_request_decorator
from ancile_web.errors import AncileException

@external_request_decorator
def test_fetch(data, token=None, **kwargs):
    data['token'] = token
    data['test_fetch'] = True
    return True


@transform_decorator
def test_transform(data):
    import time
    data['output'].append('Test Transform.')
    if data.get('test_transform', False):
        data['test_transform'].append(str(time.time()))
    else:
        data['test_transform'] = [str(time.time())]
    return True


@transform_decorator
def test_transform_param(data, param):
    import time
    data['output'].append('Test Transform with Param.')
    if data.get('test_transform_param', False):
        data['test_transform_param'].append(str(param) + str(time.time()))
    else:
        data['test_transform_param'] = [str(param) + str(time.time())]
    return True