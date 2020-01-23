from ancile.lib.federated_helpers.training import _train_local
from ancile.core.decorators import TransformDecorator
import dill

name = 'federated'



@TransformDecorator()
def train_local(data):
    unpickled = dill.loads(data)
    data = _train_local(**unpickled)
    return data
