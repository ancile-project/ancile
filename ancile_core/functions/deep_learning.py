from ancile_core.collection import reduction_fn
from ancile_core.decorators import transform_decorator, aggregate_decorator, \
    external_request_decorator
from ancile_web.errors import AncileException

name = 'test'

@external_request_decorator
def get_split_train_mnist( data, part, split, token=None, user=None, name=None):
    import torchvision
    from torchvision.transforms import transforms
    import torch

    train_ds = torchvision.datasets.MNIST('/tmp/data/', train=True, download=True, transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ]))

    # artificially splitting datasets
    chunk =  len(train_ds)//split
    print(chunk)
    if part>=chunk:
        raise Exception(f'You cannot have your id at max {chunk-1}.')
    indices = range(len(train_ds))[chunk*part:chunk*(part+1)]
    sub_dataset = torch.utils.data.Subset(train_ds, indices)
    print(len(sub_dataset))
    data['train_dataset'] = sub_dataset

    return True


@aggregate_decorator()
def aggregate_train_dataset(data):
    import torch

    ds_list = list()
    print(data)
    for user, entries in data['aggregated'].items():
        sub_ds = entries['train_dataset']
        ds_list.append(sub_ds)
    data.pop('aggregated')
    dataset = torch.utils.data.ConcatDataset(ds_list)
    data[f'train_dataset'] = dataset

    data['output'].append(f'Aggregated datasets.')
    return True

@transform_decorator
def get_loader(data, dataset_name, batch_size):
    import torch

    dataset = data[f'{dataset_name}_dataset']
    train_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
    data[f'{dataset_name}_loader'] = train_loader
    data['output'].append(f'added {dataset_name} dataset.')
    return True

@external_request_decorator
def get_test_mnist(data, token=None):
    import torchvision
    from torchvision.transforms import transforms

    data['test_dataset'] =  torchvision.datasets.MNIST('../data', train=False, download=True,
                                                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ]))

    return True


@transform_decorator
def create_model(data):
    import torch.nn as nn
    import torch.nn.functional as F

    class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.conv1 = nn.Conv2d(1, 20, 5, 1)
            self.conv2 = nn.Conv2d(20, 50, 5, 1)
            self.fc1 = nn.Linear(4 * 4 * 50, 500)
            self.fc2 = nn.Linear(500, 10)

        def forward(self, x):
            x = F.relu(self.conv1(x))
            x = F.max_pool2d(x, 2, 2)
            x = F.relu(self.conv2(x))
            x = F.max_pool2d(x, 2, 2)
            x = x.view(-1, 4 * 4 * 50)
            x = F.relu(self.fc1(x))
            x = self.fc2(x)
            return F.log_softmax(x, dim=1)

    net = Net()
    if data.get('model', False):
        data['output'].append('Loading existing model from the state')
        net.load_state_dict(data['model'])
    data['model'] = net
    data['output'].append(f'Built model')
    return True


@transform_decorator
def sgd_optimizer(data, lr, momentum):
    import torch.optim as optim
    model = data['model']
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    data['optimizer'] = optimizer
    data['output'].append(f'Created SGD model')

    return True

@transform_decorator
def nll_loss(data):
    import torch
    import torch.nn.functional as F

    data['loss'] = torch.nn.NLLLoss()

    data['output'].append(f'Created NLL Loss')

    return True

@transform_decorator
def train_one_epoch(data, epoch, log_interval=10):
    model = data['model']
    train_loader = data['train_loader']
    optimizer = data['optimizer']
    criterion = data['loss']

    model.train()
    for batch_idx, (data_batch, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data_batch)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % log_interval == 0:
            out = 'Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                       100. * batch_idx / len(train_loader), loss.item())
            print(out)

            data['output'].append(out)

@transform_decorator
def test(data, epoch):
    import torch

    model = data['model']
    test_loader = data['test_loader']
    criterion = data['loss']

    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data_batch, target in test_loader:
            output = model(data_batch)
            test_loss += criterion(output, target).item() # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True) # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    out = 'Epoch: {} Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)'.format(
        epoch, test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset))
    print(out)
    data['output'].append(out)

    return True


@transform_decorator
def get_prediction(data, image_id=1):
    import torch

    test_loader = data['test_loader']
    data = test_loader.data[image_id]
    data = data.unsqueeze(0).unsqueeze(0).type(torch.float32)
    model = data['model']
    model.eval()

    prediction = model(data)
    confidence, label = torch.max(prediction, dim=1)

    data['prediction'] = {'confidence': confidence, 'label': label}


@transform_decorator
def pickle_model(data):
    data['model'] = data['model'].state_dict()


@transform_decorator
def prepare_for_json(data):
    js = dict()
    for name, value in  data['model'].state_dict().items():
        js[name] = value.tolist()
    data['json_model'] = js


@reduction_fn
def make_dataset(collection, batch_size=20):
    from ancile_core.functions.dl.corpus import Corpus
    from ancile_core.functions.dl.helpers import batchify
    import datetime

    data = {'output': []}

    from collections import defaultdict
    locations = defaultdict(int)
    dates = defaultdict(list)
    count = 0
    for x in collection:
        if x['device_type'] == 'iPhone':
            count += 1
            name = f"x_{x['sta_location_x']}_y_{x['sta_location_y']}_floor_{x['floor_name']}"
            ft = datetime.datetime.fromtimestamp(x['aruba_system_checked_at'])
            dates[(ft.month, ft.day, ft.hour, ft.weekday())].append(name)
            locations[name] += 1

    corpus = Corpus(dates)
    train_data = batchify(corpus.train, batch_size)
    test_data = batchify(corpus.test, batch_size)
    data['corpus'] = corpus
    data['train_data'] = train_data
    data['test_data'] = test_data
    data['output'].append(f'loaded dataset. Total entries: {count}. ')

    return data


@transform_decorator
def train(data, epochs, batch_size, bptt, lr, log_interval, clip):
    from ancile_core.functions.dl.helpers import train, test, batchify
    from ancile_core.functions.dl.model import RNNModel
    import torch.nn as nn

    criterion = nn.CrossEntropyLoss()
    ntokens = len(data['corpus'].dictionary)
    corpus = data['corpus']
    train_data = batchify(corpus.train, batch_size)
    test_data = batchify(corpus.test, batch_size)

    model = RNNModel("LSTM", ntokens, 50, 50, 2, 0.1, True)
    for epoch in range(epochs):
        train(model, train_data, ntokens, batch_size, bptt, criterion, epoch, lr, log_interval, clip)
        acc = test(model, test_data,  ntokens, batch_size, bptt, criterion, epoch)
        data['output'].append(acc)

    data['model'] = model


@transform_decorator
def train_dp(data, epochs, batch_size, bptt, lr, log_interval, sigma, S):
    from ancile_core.functions.dl.helpers import train_dp, test, batchify
    from ancile_core.functions.dl.model import RNNModel
    from ancile_core.functions.dl.compute_dp_sgd_privacy import apply_dp_sgd_analysis
    import torch.nn as nn


    criterion = nn.CrossEntropyLoss()
    criterion_dp = nn.CrossEntropyLoss(reduction='none')
    ntokens = len(data['corpus'].dictionary)
    corpus = data['corpus']
    train_data = batchify(corpus.train, batch_size)
    test_data = batchify(corpus.test, batch_size)

    N = train_data.shape[0]
    eps = apply_dp_sgd_analysis(N=N, batch_size=batch_size, noise_multiplier=sigma*S, epochs=epochs)
    data['output'].append(f"Epsilon: {eps}")

    model = RNNModel("LSTM", ntokens, 50, 50, 2, 0.1, True)

    for epoch in range(epochs):
        train_dp(model, train_data, ntokens, batch_size, bptt, criterion_dp, epoch, lr, log_interval, S, sigma)
        acc = test(model, test_data,  ntokens, batch_size, bptt, criterion, epoch)
        data['output'].append(acc)

    data['model'] = model

