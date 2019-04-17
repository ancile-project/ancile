import requests
import json
from cryptography.fernet import Fernet

js = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWEBZAAGc2lnbmVkbgYArMeRtWkB.3v5L3WHsMFfgsmxnyHyYSZiFhb7T5pdT8iDNrgh0DrI",
    "users": ["user1@abcd.com"],
    "purpose": "research",
    "program": """
dp_1 = user_specific["user1@abcd.com"].get_empty_data_pair(data_source='test')
test.test_transform(data=dp_1)
test.test_transform(data=dp_1)
general.flatten(data=dp_1)
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


js2 = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWEBZAAGc2lnbmVkbgYArMeRtWkB.3v5L3WHsMFfgsmxnyHyYSZiFhb7T5pdT8iDNrgh0DrI",
    "users": ["user1@abcd.com"],
    "purpose": "research",
    "persisted_dp_uuid": new_js['persisted_dp_uuid'],
    "program": """
dp_1 = user_specific["user1@abcd.com"].retrieve_existing_dp_pair(data_source='test')
test.test_transform(data=dp_1)
test.test_transform(data=dp_1)
general.flatten(data=dp_1)
result.append_dp_data_to_result(data=dp_1, decrypt_field_list=["test_transform", "test_transform2"])
    """
}

res2 = requests.post('http://localhost:5000/api/run', json=js2)
new_js2 = res2.json()
if new_js2.get('result', False) == 'error':
    print(new_js2['traceback'])
else:
    print(json.dumps(new_js2, indent=4))
#
# for key, value in new_js['encrypted_data'].items():
#     for key2, value2 in value.items():
#         for key3, value3 in value2.items():
#             print(value3)
#             enc_key = new_js2['encryption_keys'][key][key2][key3]
#             f = Fernet(enc_key.encode('utf-8'))
#             print(f.decrypt(value3.encode('utf-8')))
