from ancile.core.primitives import DataPolicyPair, Collection, Policy
import logging
from ancile.core.decorators import *

from ancile.utils.errors import AncileException, PolicyError

logger = logging.getLogger(__name__)


class ReductionDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('reduction')

    def process_call(self, command):

        logger.debug(f'Calling Reduction "{command.function_name}"')

        collection = command.params.get('collection', None)
        if not isinstance(collection, Collection):
            raise AncileException('Please provide a Collection object as `collection` argument.')
        policy = Policy(collection.get_collection_policy().advance_policy(command))
        if not policy:
            raise PolicyError(f'Collection policy prevented execution of \'{f.__name__}\'')

        command.params['collection'] = [x._data for x in collection._data_points]
        data = command.call()
        dp = DataPolicyPair(policy, None, 'reduce', None, None)
        dp._data = data

        return dp

