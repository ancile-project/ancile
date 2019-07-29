import wrapt
import logging
logger = logging.getLogger(__name__)
from ancile.core.decorators import *


class UseDecorator(BaseDecorator):

    @wrapt.decorator
    def process_call(command, is_collection):
        logger.debug('Calling Use Decorator')

        return True
