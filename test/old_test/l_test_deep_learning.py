import requests
import json

js = {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzYWx0IjoiXFx4MjQzMjYyMjQzMTMyMjQ0ODMwNDk0NDM5NzY2ZDcxNDQ2MzRkMmY2ZjM3NzU3YTYyNzgyZTc3NjgyZSJ9.vxTjpAIX-GwvnLS5n1j2owa-LcZWcxAtN_yWCDu2X8I",
    "users": ["user"],
    "purpose": "research",
    "program": """
path = '/Users/ebagdasaryan/Documents/development/ancile/location_dump.json'

dp_1 = indoor_location.preload_location(user=user("user"), path=path)

deep_learning.make_dataset(data=dp_1)
deep_learning.train(data=dp_1, epochs=10, batch_size=20, bptt=20, lr=2, log_interval=5, clip=0.25)

#deep_learning.train_dp(data=dp_1, epochs=10, batch_size=20, bptt=20, lr=0.2, log_interval=5, sigma=0.8, S=1)

general.keep_keys(data=dp_1, keys=['output'])

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
