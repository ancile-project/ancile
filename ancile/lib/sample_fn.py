"""
This module defines Ancile fake test functions that have no impact on data, but
can be used for testing purposes.
"""
from core.decorators import transform_decorator


# This currently won't work because of how DPPs are created normally and how
# the proper token is routed to the function.
# @external_request_decorator()
# def fetch_test_data(target_url=None, user=None):
#     from ancile_core.functions.general import get_token
#     data = {'output': []}
#     token = get_token(user)
#     print(f"FUNC: fetch_test_data: {target_url}, {token}")
#     data['fetch_test_data'] = True
#     return data


@transform_decorator
def test_transform(data):
    import time
    data['output'].append('Test Transform.')
    if data.get('test_transform', False):
        data['test_transform'].append(str(time.time()))
    else:
        data['test_transform'] = [str(time.time())]


@transform_decorator
def test_transform_param(data, param):
    import time
    data['output'].append('Test Transform with Param.')
    if data.get('test_transform_param', False):
        data['test_transform_param'].append(str(param) + str(time.time()))
    else:
        data['test_transform_param'] = [str(param) + str(time.time())]