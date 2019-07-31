import wrapt
from ancile.core.decorators import *
import logging
logger = logging.getLogger(__name__)


class AggregateDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False, reduce=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('aggregate')

    @staticmethod
    def process_call(command, is_collection):
        logger.debug('Calling Aggregate Decorator')

        return NotImplemented
