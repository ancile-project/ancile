import requests
import json

js = {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzYWx0IjoiXFx4MjQzMjYyMjQzMTMyMjQ0ODMwNDk0NDM5NzY2ZDcxNDQ2MzRkMmY2ZjM3NzU3YTYyNzgyZTc3NjgyZSJ9.vxTjpAIX-GwvnLS5n1j2owa-LcZWcxAtN_yWCDu2X8I",
    "users": ["user"],
    "purpose": "research",
    "program": """
#dp_1 = user("user").get_empty_data_pair(data_source='test')
#dp_2 = user("user").get_empty_data_pair(data_source='test')

dp_1 = deep_learning.get_split_train_mnist(user=user("user"), name='test', split=2, part=0)
dp_2 = deep_learning.get_split_train_mnist(user=user("user"), name='test', split=2, part=1) 

coll = new_collection()
coll.add_to_collection(data=dp_1)
coll.add_to_collection(data=dp_2)

collection=coll

deep_learning.get_test_mnist(data=aggr_dp)

deep_learning.get_loader(data=aggr_dp, dataset_name='train', batch_size=64)
deep_learning.get_loader(data=aggr_dp, dataset_name='test', batch_size=100)

deep_learning.create_model(data=aggr_dp)
deep_learning.sgd_optimizer(data=aggr_dp, lr=0.1, momentum=0.9)
deep_learning.nll_loss(data=aggr_dp)
 
deep_learning.pickle_model(data=aggr_dp)
#for epoch in range(1):
#    deep_learning.train_one_epoch(data=aggr_dp, epoch=epoch, log_interval=200)
#    deep_learning.test(data=aggr_dp, epoch=epoch)

#general.keep_keys(data=aggr_dp, keys=['output'])
#result.append_dp_data_to_result(data=aggr_dp)

    """
}

res = requests.post('http://localhost:5000/api/run', json=js)

print(res.status_code)
new_js = res.json()
if new_js.get('result', False) == 'error':
    print(new_js['traceback'])
else:
    print(json.dumps(new_js, indent=4))
