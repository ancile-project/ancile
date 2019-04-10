import requests
import json

js = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWECZAAGc2lnbmVkbgYAEDg9vWkB.h-iDyUq7B9aHw4Bp7UmOShtuFysIELHZb_uyuzx8OnU",
    "users": ["user1@abcd.com"],
    "purpose": "research",
    "program": """
dp_1 = user_specific["user1@abcd.com"].get_empty_data_pair(data_source='campus_data_service')
indoor_location.fetch_location(data=dp_1)
test.test_transform(data=dp_1)
test.test_transform(data=dp_1)
general.keep_path_keys(data=dp_1, path="location", keys=["floor_name"])
result.append_dp_data_to_result(data=dp_1)
    """
}

res = requests.post('http://dev.ancile.smalldata.io:5000/api/run', json=js)

print(res.status_code)
new_js = res.json()
if new_js.get('result', False) == 'error':
    print(new_js['traceback'])
else:
    print(json.dumps(new_js, indent=4))
