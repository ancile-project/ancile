from ancile.core.decorators import *
from ancile.lib.general import get_token
from ancile.utils.errors import AncileException
import requests

name = 'rdl'


@ExternalDecorator()
def test_fetch(user=None, **kwargs):
    data = {'output': []}
    token = get_token(user)
    data['token'] = token
    data['test_fetch'] = True

    return data


@ExternalDecorator()
def rdl_fetch(user=None, **kwargs):
    data = {'output': []}
    token = get_token(user)

    r = requests.get('https://localhost:9980/test/api/usage',
                     headers={'Authorization': f'Bearer {token}'})

    if r.status_code == 200:
        data.update(r.json())
        print(r.json())
        print(data)
    else:
        raise AncileException(f"Request error: {r.json()}")

    return data

@TransformDecorator()
def test_transform(data):
    import time
    data['output'].append('Test Transform.')
    if data.get('test_transform', False):
        data['test_transform'].append(str(time.time()))
    else:
        data['test_transform'] = [str(time.time())]
    print(data)
    return data


@TransformDecorator()
def test_transform_param(data, param):
    import time
    data['output'].append('Test Transform with Param.')
    if data.get('test_transform_param', False):
        data['test_transform_param'].append(str(param) + str(time.time()))
    else:
        data['test_transform_param'] = [str(param) + str(time.time())]
    return data
