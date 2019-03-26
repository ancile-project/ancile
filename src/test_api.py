import requests
import json

js = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWEBZAAGc2lnbmVkbgYArMeRtWkB.3v5L3WHsMFfgsmxnyHyYSZiFhb7T5pdT8iDNrgh0DrI",
    "user": "user1@abcd.com",
    "purpose": "research",
    "program": """
dp_1 = user_specific.get_empty_data_pair(data_source='campus_data_service')
indoor_location.fetch_location(data=dp_1)
test.test_transform(data=dp_1)
test.test_transform(data=dp_1)
result.append_dp_data_to_result(data=dp_1)
    """
}

res = requests.post('http://127.0.0.1:5000/api/run', json=js)

print(res.status_code)
new_js = res.json()
if new_js.get('result', False) == 'error':
    print(new_js['traceback'])
else:
    print(new_js)
