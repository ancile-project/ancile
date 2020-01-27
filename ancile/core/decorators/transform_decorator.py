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
        #logger.debug(f'Calling Transformation "{command.function_name}" with arguments {command.print_params}')

        dp_pairs = TransformDecorator.decorator_preamble(command.params)
        if len(dp_pairs) == 1:
            key, dp_pair = dp_pairs.popitem()
            new_dp_pair = copy.copy(dp_pair)
            new_dp_pair._data = new_dp_pair._call_transform(command=command, keys=key)
            #logger.error(new_dp_pair._data)
        else:
            new_dp_pair = DataPolicyPair.combine_dpps_dict(dp_pairs)
            new_dp_pair._data = new_dp_pair._call_transform(command=command, keys=list(dp_pairs.keys()))
            #logger.error(new_dp_pair._data)
        return new_dp_pair

    @staticmethod
    def decorator_preamble(params):
        dp_pairs = dict()

        for name, param in params.items():
            if isinstance(param, DataPolicyPair):
                #logger.info(f'Found DataPolicyPair for param: {name}')
                dp_pairs[name] = param
            elif isinstance(param, list):
                # check all items in list are DPPs
                if len(param) == len([True for i in param if isinstance(i, DataPolicyPair)]):
                    dp_pairs[name] = DataPolicyPair.combine_dpps_list(param)

        if len(dp_pairs) == 0:
            logger.info(f'Calling function without DPPs')
            raise AncileException("Passed no DataPolicyPairs. Not Implemented yet.")

        return dp_pairs
