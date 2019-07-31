import wrapt
from ancile.core.decorators import *
import logging
logger = logging.getLogger(__name__)


class FilterDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('filter')

    @staticmethod
    def process_call(command, is_collection):
        logger.debug('Calling Filter Decorator')

        return NotImplemented
