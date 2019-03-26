from src.micro_data_core_python.decorators import transform_decorator, external_request_decorator
from src.micro_data_core_python.errors import AncileException

@external_request_decorator
def fetch_location(data, token=None):
    import requests
    import datetime

    data['token'] = token
    data['test_fetch'] = True
    url = "https://campus.cornelltech.io/api/location/mostrecent/"
    headers = {'Authorization': "Bearer " + token}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data['location'] = res.json()
        data['location']['timestamp'] = datetime.datetime.fromtimestamp(data['location']['timestamp'])
        data['location']['aruba_system_checked_at'] = datetime.datetime.fromtimestamp(data['location']['aruba_system_checked_at'])
    else:
        raise AncileException("Couldn't fetch location from the server.")

    return True


@transform_decorator
def test_transform(data):
    import time

    data['test_transform_' + str(time.time())] = True
    return True