import copy
import logging
logger = logging.getLogger(__name__)
from ancile.core.decorators import *


class TransformDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('transform')

    @staticmethod
    def process_call(command, is_collection):
        logger.debug('Calling Transform Decorator')

        dp_pair = TransformDecorator.decorator_preamble(command.params)
        new_dp_pair = copy.copy(dp_pair)
        new_dp_pair._data = new_dp_pair._call_transform(command)

        return new_dp_pair
