import requests
import json

js = {
    "token": "SFMyNTY.g3QAAAACZAAEZGF0YWEBZAAGc2lnbmVkbgYArMeRtWkB.3v5L3WHsMFfgsmxnyHyYSZiFhb7T5pdT8iDNrgh0DrI",
    "users": ["user1@abcd.com", "user2@abcd.com"],
    "purpose": "research",
    "program": """
dp_1 = user_specific["user1@abcd.com"].get_empty_data_pair(data_source='test')
dp_2 = user_specific["user2@abcd.com"].get_empty_data_pair(data_source='test')

deep_learning.get_split_train_mnist(data=dp_1, split=2, part=0)
deep_learning.get_split_train_mnist(data=dp_2, split=2, part=1) 

aggr_dp = deep_learning.aggregate_train_dataset(data=[dp_1, dp_2])

deep_learning.get_test_mnist(data=aggr_dp)

deep_learning.get_loader(data=aggr_dp, dataset_name='train', batch_size=64)
deep_learning.get_loader(data=aggr_dp, dataset_name='test', batch_size=100)

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
