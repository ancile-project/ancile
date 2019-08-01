import logging
from ancile.core.decorators import *
from ancile.core.primitives import *

logger = logging.getLogger(__name__)

# Helper Comparison Functions
def _dependent_comparison(**kwargs):
    pass

def _enforce_comparison(**kwargs):
    pass



class ComparisonDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('compare')

    def process_call(self, command):
        logger.debug('Calling Comparison Decorator')

        dp_pair = self.decorator_preamble(command.params)

        dependent = command.params.pop('dependent_dp', False)

        if isinstance(dependent, DataPolicyPair):
            dependent_command = Command(_dependent_comparison)
            dependent_command.params.update(command.params)
            dependent_command.params.update(dp_pair.metadata)
            command.params.update(dependent.metadata)
            dp_pair._resolve_private_data_keys(command.params)
            dependent._advance_policy_error(dependent_command)

            dp_pair._advance_policy_error(command)
            dp_pair._resolve_private_data_values(command.params)

            command.params['data'] = dependent._data
            result = command.call()
            enforcement_command = Command(_enforce_comparison, scopes=None,
                                          params={'result': result})
            dp_pair._advance_policy_error(enforcement_command)
        else:
            result = dp_pair._call_transform(command)
            enforcement_command = Command(_enforce_comparison, scopes=None,
                                          params={'result': result})
            dp_pair._advance_policy_error(enforcement_command)

        return result
