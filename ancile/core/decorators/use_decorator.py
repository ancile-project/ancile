from ancile.core.decorators import *
import logging
import copy
logger = logging.getLogger(__name__)


class UseDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('return')

    def process_call(self, command):
        #logger.debug(f'Calling Use "{command.function_name}" with arguments {command.print_params}')

        dp_pair = UseDecorator.decorator_preamble(command.params)
        new_dp_pair = copy.copy(dp_pair)
        ret = new_dp_pair._use_method(command)

        # @TODO: fix later
        # if new_dp_pair._was_loaded:
        #     storage.del_key(dp_pair._load_key)
        return ret
