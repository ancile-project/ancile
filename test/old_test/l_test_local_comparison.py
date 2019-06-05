import requests
import json
from cryptography.fernet import Fernet

js = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWEBZAAGc2lnbmVkbgYArMeRtWkB.3v5L3WHsMFfgsmxnyHyYSZiFhb7T5pdT8iDNrgh0DrI",
    "users": ["user1@abcd.com"],
    "purpose": "research",
    "program": """
#dp_1 = user_specific["user1@abcd.com"].get_empty_data_pair(data_source='test')

sample_policy="test_fetch.test_transform.test_transform.flatten.(release_comparison + return)"

dp_1 = test.test_fetch(user_specific=user_specific["user1@abcd.com"], data_source='test',  sample_policy=sample_policy)
test.test_transform(data=dp_1)
test.test_transform(data=dp_1)
general.flatten(data=dp_1)
res = use_type.release_field_comparison(data=dp_1, field_path='test_fetch', comparison_operator='eq', value=True)
if not res:
    result.append_dp_data_to_result(data=dp_1)
else:
    result.append_keys_to_result(data=dp_1)

    """
}

res = requests.post('http://localhost:5000/api/run', json=js)

print(res.status_code)
new_js = res.json()
if new_js.get('result', False) == 'error':
    print(new_js['traceback'])
else:
    print(json.dumps(new_js, indent=4))