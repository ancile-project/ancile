from src.micro_data_core_python.decorators import external_request_decorator
from src.micro_data_core_python.errors import AncileException


@external_request_decorator
def fetch_test_data(data=None, target_url=None, token=None):
    print(f"FUNC: fetch_test_data: {target_url}, {token}")
    data['fetch_test_data'] = True
    return True

@external_request_decorator
def get_data(data, target_url=None, token=None):
    import requests
    # print("FUNC: SIMPLE_API")
    # print("  target_url: " + target_url)

    r = requests.get(target_url, headers={'Authorization': "Bearer " + token})

    if r.status_code == 200:
        data.update(r.json()) # Need to maintain given dict
    else:
        print(r.status_code)
        raise AncileException("Request error")

@external_request_decorator
def full_api(data, body=None, target_url=None, token=None):
    ## INCOMPLETE

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