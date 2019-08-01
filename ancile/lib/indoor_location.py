from ancile.core.decorators import *
from ancile.lib.general import get_token
from ancile.utils.errors import AncileException

name="location"


@ExternalDecorator()
def fetch_location(user, device_type=None):
    import requests
    import datetime
    import pytz

    token = get_token(user)
    print(token)
    data = {'output': []}
    data['output'].append(token)

    eastern = pytz.timezone('US/Eastern')
    data['token'] = token
    data['test_fetch'] = True
    url = "https://campus.cornelltech.io/api/location/mostrecent/"
    payload = {'device_type': device_type}
    headers = {'Authorization': "Bearer " + token}
    res = requests.get(url, headers=headers, params=payload)
    if res.status_code == 200:
        data['location'] = res.json()
        ts = datetime.datetime.fromtimestamp(data['location']['timestamp'], tz=pytz.utc)
        loc_dt = ts.astimezone(eastern)
        data['location']['timestamp'] = loc_dt.strftime("%c")
    else:
        raise AncileException("Couldn't fetch location from the server.")

    return data


@ExternalDecorator(is_collection=True)
def preload_location(user, path=None):
    import json

    data = list()

    with open(path, 'r') as f:
        data.extend(json.load(f))

    return data


@ExternalDecorator()
def fetch_history_location(data, token=None, fr=None, to=None, device_type=None):
    import requests
    import datetime
    import pytz

    eastern = pytz.timezone('US/Eastern')

    data['token'] = token
    data['test_fetch'] = True
    url = "https://campus.cornelltech.io/api/location/history/"
    headers = {'Authorization': "Bearer " + token}
    payload = {'from': fr, 'to': to, 'device_type': device_type}
    res = requests.get(url, headers=headers, params=payload)
    if res.status_code == 200:
        parsed_data = list()
        for entry in res.json()['data']:
            ts = datetime.datetime.fromtimestamp(entry['timestamp'], tz=pytz.utc)
            loc_dt = ts.astimezone(eastern)
            entry['timestamp'] = loc_dt.strftime("%c")
            parsed_data.append(entry)
        data['location'] = sorted(parsed_data, key=lambda x: x['timestamp'])
    else:
        raise AncileException("Couldn't fetch location from the server.")

    return True


@TransformDecorator()
def test_transform(data):
    import time

    data['test_transform_' + str(time.time())] = True
    return True


@TransformDecorator()
def fuzz_location(data, mean, std):
    import numpy as np

    data['sta_location_x'] = np.random.normal(mean, std)
    data['sta_location_y'] = np.random.normal(mean, std)
