import requests
import json

js = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWEBZAAGc2lnbmVkbgYArMeRtWkB.3v5L3WHsMFfgsmxnyHyYSZiFhb7T5pdT8iDNrgh0DrI",
    "users": ["user1@abcd.com", "user2@abcd.com"],
    "purpose": "research",
    "persisted_dp_uuid": "8b854906-5a1e-11e9-bd6d-8c85902f5c4d",
    "program": """

aggr_dp = user_specific['aggregated'].retrieve_existing_dp_pair(data_source='aggregated')
deep_learning.create_model(data=aggr_dp)
deep_learning.sgd_optimizer(data=aggr_dp, lr=0.1, momentum=0.9)
deep_learning.nll_loss(data=aggr_dp)

for epoch in range(1):
    deep_learning.train_one_epoch(data=aggr_dp, epoch=epoch, log_interval=200)
    deep_learning.test(data=aggr_dp, epoch=epoch)

general.keep_keys(data=aggr_dp, keys=['output'])
result.append_dp_data_to_result(data=aggr_dp)

    """
}

res = requests.post('http://localhost:5000/api/run', json=js)

print(res.status_code)
new_js = res.json()
if new_js.get('result', False) == 'error':
    print(new_js['traceback'])
else:
    print(json.dumps(new_js, indent=4))
