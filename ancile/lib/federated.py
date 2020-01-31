from ancile.lib.federated_helpers.training import _train_local
from ancile.core.decorators import TransformDecorator
import dill

name = 'federated'


@TransformDecorator()
def train_local(model, data_point):
    """
    This part simulates the

    """
    unpickled = dill.loads(model)
    unpickled["train_data"] = data_point
    output = _train_local(**unpickled)
    data = dill.dumps(output)
    return data


@TransformDecorator()
def accumulate(incoming_dp, summed_dps):
    import torch
    # averaging part
    incoming_dp = dill.loads(incoming_dp)
    for name, data in incoming_dp.items():
        #### don't scale tied weights:
        if name == 'decoder.weight' or '__' in name:
            continue
        if summed_dps.get(name, False) is False:
            summed_dps[name] = torch.zeros_like(data, requires_grad=True)
        with torch.no_grad():
            summed_dps[name].add_(data)

    return summed_dps


@TransformDecorator()
def average(summed_dps, global_model, eta, diff_privacy=None):
    import torch

    for name, data in global_model.items():
        #### don't scale tied weights:
        if name == 'decoder.weight' or '__' in name:
            continue

        update_per_layer = summed_dps[name] * eta
        if diff_privacy:
            noised_layer = torch.cuda.FloatTensor(data.shape).normal_(mean=0, std=diff_privacy['sigma'])
            update_per_layer.add_(noised_layer)

        with torch.no_grad():
            data.add_(update_per_layer)

    return global_model
