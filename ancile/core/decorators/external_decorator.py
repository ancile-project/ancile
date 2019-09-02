import logging
import inspect
from ancile.core.decorators import *
from ancile.core.user_secrets import UserSecrets

logger = logging.getLogger(__name__)


class ExternalDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('fetch')

    def process_call(self, command):
        logger.debug(f'Calling External "{command.function_name}" with arguments {command.print_params}')

        user_specific = command.params.pop('user', False)
        data_source = inspect.getmodule(command.function).name
        name = command.params.pop('name', False)
        sample_policy = command.params.pop('sample_policy', '(ANYF*).return')

        if not isinstance(user_specific, UserSecrets):
            raise ValueError("You have to provide a UserSpecific object to fetch new data.")

        dp_pair = user_specific.get_empty_data_pair(data_source, name=name, sample_policy=sample_policy)
        dp_pair._data = dp_pair._call_external(command)

        return dp_pair

    @staticmethod
    def check_dp_pair_passed(args, kwargs):
        """
        Ignore this check as external commands don't need DPPs.
        """

        return True



