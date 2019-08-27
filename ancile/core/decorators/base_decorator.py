from abc import ABC, abstractmethod
import wrapt

from ancile.core.primitives.command import Command
import inspect

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
        if callable(scopes):
            raise ValueError(f'You probably defined the decorator without '
                             f'parenthesis. Check function: {scopes}. '
                             f'Try: {self.__class__.__name__}()')
        self.is_collection = is_collection
        self.scopes = scopes if scopes else list()
        self.decorated = True

    @wrapt.decorator
    def __call__(self, wrapped, _, args, kwargs):
        """
        We check if the call to the method was
        originated from the submitted program (has signature <string>)
        or from library module. If the call comes from the library
        we can ignore the checks and keep the library operational.

        Example: numpy.sort() uses methods amin(), amax() a lot, so we don't need
        to put amin and amax in the policy.
        """

        context = inspect.stack()
        if context[1].filename == '<string>':
            if args:
                raise ValueError("Please specify keyword arguments instead of positions.")
            command = Command(function=wrapped, scopes=self.scopes, params=kwargs)
            return self.process_call(command)
        else:
            wrapped(*args, **kwargs)

    @abstractmethod
    def process_call(self, command: Command):
        pass

    @staticmethod
    def check_data(dp_pair):
        from ancile.core.primitives import DataPolicyPair

        if not isinstance(dp_pair, DataPolicyPair):
            raise ValueError(f"You need to provide a Data object. "
                             f"Use get_data to get it. Received: {dp_pair}")

    @staticmethod
    def decorator_preamble(params):

        dp_pair = params.get('data', False)
        BaseDecorator.check_data(dp_pair)
        return dp_pair
