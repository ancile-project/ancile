from abc import ABC, abstractmethod
import wrapt

from ancile.core.primitives.policy_helpers.command import Command


class BaseDecorator(ABC):
    """
    This is the Base class for all new decorators. It uses wrapt module to
    interrupt the calls.
    """

    def __init__(self, scopes=None, is_collection=False):
        """

        :param scopes: we can use this parameter to add aliases to functions,
         such as data source name, function type, etc.
        :param is_collection: not implemented, but can be a flag that the input
        is a collection
        """
        self.is_collection = is_collection
        self.scopes = scopes if scopes else list()

    @wrapt.decorator
    def __call__(self, wrapped, _, args, kwargs):
        if args:
            raise ValueError("Please specify keyword arguments instead of positions.")
        command = Command(function=wrapped, scopes=self.scopes, params=kwargs)
        return self.__class__.process_call(command, self.is_collection)

    @staticmethod
    @abstractmethod
    def process_call(command: Command, is_collection: bool):
        pass

    @staticmethod
    def check_data(dp_pair):
        from ancile.core.primitives import DataPolicyPair

        if not isinstance(dp_pair, DataPolicyPair):
            raise ValueError("You need to provide a Data object. Use get_data to get it.")

    @staticmethod
    def decorator_preamble(params):

        dp_pair = params.get('data', False)
        BaseDecorator.check_data(dp_pair)
        return dp_pair
