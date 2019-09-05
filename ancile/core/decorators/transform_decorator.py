import copy
from ancile.core.decorators import *
import logging

from ancile.core.primitives import DataPolicyPair
from ancile.utils.errors import AncileException

logger = logging.getLogger(__name__)


class TransformDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('transform')

    def process_call(self, command):
        logger.debug(f'Calling Transformation "{command.function_name}" with arguments {command.print_params}')

        dp_pairs = TransformDecorator.decorator_preamble(command.params)
        if len(dp_pairs) == 1:
            name, dp_pair = dp_pairs[0]
            new_dp_pair = copy.copy(dp_pair)
            new_dp_pair._data = new_dp_pair._call_transform(command=command, key=key)
            logger.error(new_dp_pair._data)
        else:
            raise NotImplemented
        return new_dp_pair

    @staticmethod
    def decorator_preamble(params):
        dp_pairs = list()

        for name, param in params.items():
            if isinstance(param, DataPolicyPair):
                logger.info(f'Found DataPolicyPair for param: {name}')
                dp_pairs.append((name, param))

        if len(dp_pairs) == 0:
            logger.info(f'Calling function without DPPs')
            raise AncileException("Passed no DataPolicyPairs. Not Implemented yet.")

        return dp_pairs
