from ancile.core.decorators import *
from ancile.lib.general import get_token
from ancile.utils.errors import AncileException

name="databox"


@ExternalDecorator()
def get_latest_reddit_data(user, session):
    import requests
    import dill

    url = "https://127.0.0.1/app-ancile/ui/tsblob/latest"
    payload = { "data_source_id": "redditSimulatorData"}
    headers = { "session": session }
    res = requests.get(url, cookies=headers, params=payload, verify=False)
    if res.status_code == 200:
        data = res.json()
    else:
        raise AncileException("Couldn't fetch data from databox.")
    string = data['data'][0]['data']['data']
    print(string, flush=True)
    return string
