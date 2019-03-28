from src.micro_data_core_python.decorators import transform_decorator, external_request_decorator
from src.micro_data_core_python.errors import AncileException

@external_request_decorator
def test_fetch(data, token=None):
    data['token'] = token
    data['test_fetch'] = True
    return True


@transform_decorator
def test_transform(data):
    import time

    data['test_transform_' + str(time.time())] = True
    return True