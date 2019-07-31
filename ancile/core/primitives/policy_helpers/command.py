import traceback
import logging
import inspect
from ancile.utils.errors import AncileException
logger = logging.getLogger(__name__)


class Command:
    """
    A class that represents the policy_command called from the program

    """

    def __init__(self, function, scopes=None, params=None):
        """

        :param function: function object
        :param scopes: a list of function scope that can include
            function type (e.g. transform, return)
            or a module name (e.g. google, outlook)

        :param params: a dictionary with provided function arguments
        """
        self.function = function
        self.function_name = function.__name__
        self.scopes = scopes if scopes is not None else list()
        self.params = params if params is not None else dict()
        module = inspect.getmodule(function)
        if hasattr(module, 'name'):
            self.scopes.append(module.name)

    def __repr__(self):

        return f'<? COMMAND: function: {self.function_name}, scopes: {self.scopes}, params: {self.params}>'

    def call(self):
        """
        Call the function
        """
        try:
            result = self.function(**self.params)
            return result
        except:
            error = f"Error executing function: {self.function_name}(). Log: {traceback.format_exc()}"
            logger.error(error)
            raise AncileException(error)
