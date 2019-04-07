import requests
import json

js = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWEBZAAGc2lnbmVkbgYArMeRtWkB.3v5L3WHsMFfgsmxnyHyYSZiFhb7T5pdT8iDNrgh0DrI",
    "users": ["user1@abcd.com", "user2@abcd.com"],
    "purpose": "research",
    "program": """
dp_1 = user_specific["user1@abcd.com"].get_empty_data_pair(data_source='campus_data_service')
dp_2 = user_specific["user2@abcd.com"].get_empty_data_pair(data_source='test')
indoor_location.fetch_location(data=dp_1)
if dp_1.check_command_allowed('transform'):
    test.test_transform(data=dp_1)
#test.test_transform(data=dp_2)
#dp_3 = general.basic_aggregation(data=[dp_1,dp_2])
#if dp_1.check_command_allowed('help'):
result.append_dp_data_to_result(data=dp_1)
    """
}

res = requests.post('http://localhost:5000/api/run', json=js)

print(res.status_code)
new_js = res.json()
if new_js.get('result', False) == 'error':
    print(new_js['traceback'])
else:
    print(json.dumps(new_js, indent=4))
