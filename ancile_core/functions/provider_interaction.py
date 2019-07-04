from ancile_core.decorators import external_request_decorator
from ancile_core.functions.general import get_token
from ancile_web.errors import AncileException


@external_request_decorator
def fetch_test_data(target_url=None, user=None):
    data = {'output': []}
    token = get_token(user)
    print(f"FUNC: fetch_test_data: {target_url}, {token}")
    data['fetch_test_data'] = True
    return data

@external_request_decorator
def get_data(target_url=None, user=None):
    import requests

    data = {'output': []}
    token = get_token(user)

    r = requests.get(target_url, headers={'Authorization': "Bearer " + token})

    if r.status_code == 200:
        data.update(r.json()) # Need to maintain given dict
    else:
        print(r.status_code)
        raise AncileException("Request error")

    return data

@external_request_decorator
def full_api(user, body=None, target_url=None):

    data = {'output': []}
    token = get_token(user)

    import requests
    print("FUNC: FULL_API")
    print("  target_url: " + target_url)
    print("        body: " + str(body))

    r = requests.get(target_url, headers={'Authorization': "Bearer " + token},
                     body=body)

    if r.status_code == 200:
        data.update(r.json()) # Need to maintain given dict
    else:
        print(r.status_code)
        raise AncileException("Request error")

    return data