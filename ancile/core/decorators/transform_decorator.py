import copy
from ancile.core.decorators import *
import logging
logger = logging.getLogger(__name__)


class TransformDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('transform')

    def process_call(self, command):
        logger.debug(f'Calling Transformation "{command.function_name}" with arguments {command.print_params}')

        dp_pair = TransformDecorator.decorator_preamble(command.params)
        new_dp_pair = copy.copy(dp_pair)
        new_dp_pair._data = new_dp_pair._call_transform(command)

        return new_dp_pair
