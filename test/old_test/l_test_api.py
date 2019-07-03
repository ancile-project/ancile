import requests
import json

js = {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzYWx0IjoiXFx4MjQzMjYyMjQzMTMyMjQ0ODMwNDk0NDM5NzY2ZDcxNDQ2MzRkMmY2ZjM3NzU3YTYyNzgyZTc3NjgyZSJ9.vxTjpAIX-GwvnLS5n1j2owa-LcZWcxAtN_yWCDu2X8I",
    "users": ["user"],
    "purpose": "research",
    "program": """
#dp_1 = user_specific["user1@abcd.com"].get_empty_data_pair(data_source='campus_data_service')
dp_1 = indoor_location.fetch_location(user=user('user'))
#test.test_transform(data=dp_1)
#test.test_transform(data=dp_1)
#general.keep_path_keys(data=dp_1, path="location", keys=["floor_name"])
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
