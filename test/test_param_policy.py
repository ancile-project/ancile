import requests
import json
from cryptography.fernet import Fernet

js = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWEBZAAGc2lnbmVkbgYArMeRtWkB.3v5L3WHsMFfgsmxnyHyYSZiFhb7T5pdT8iDNrgh0DrI",
    "users": ["user1@abcd.com"],
    "purpose": "research",
    "program": """
dp_1 = user_specific["user1@abcd.com"].get_empty_data_pair(data_source='test', sample_policy='test_transform_param(param="param").return')
test.test_transform_param(data=dp_1, param="param")
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