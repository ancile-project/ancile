import wrapt
import logging
import copy
logger = logging.getLogger(__name__)
from ancile.core.decorators import *
import ancile.core.advanced.storage as storage


class ComparisonDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('compare')

    @staticmethod
    def process_call(command, is_collection):
        logger.debug('Calling Comparison Decorator')

        return NotImplemented