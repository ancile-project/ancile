from ancile.core.primitives.policy_helpers.expressions import *


class ExecExpression(BaseExpression):

    def __init__(self, command: str, params=None):
        super().__init__()
        self.policy_command = command
        self.params = params

    def __repr__(self):
        if self.params:
            return f'{self.policy_command}({", ".join([str(x) for x in self.params.values()])})'
        else:
            return f'{self.policy_command}'

    def __eq__(self, other):
        if isinstance(other, self.__class__) \
                and self.policy_command == other.policy_command \
                and self.params == other.params:
            return True
        else:
            return False

    def d_step(self, command):
        """
        D(C, C) = 1
        D(C', C) = 0

        The policy might specify a scope (e.g. transform, return) instead of a
        real function name, therefore we as well check if policy_command is
        present among command.scopes.

        As well, we check only parameters that the policy specifies, otherwise
        we accept any value for the parameter.

        """
        if self.policy_command == 'ANYF':
            return ConstantExpression(Constants.ONE)
        elif self.policy_command == command.function_name or \
                self.policy_command in command.scopes:

            for key, value in command.params.items():
                if key == 'data':
                    continue
                proposed_value = command.params.get(key, None)
                if not value.evaluate(proposed_value):
                    return ConstantExpression(Constants.ZERO)

            return ConstantExpression(Constants.ONE)
        else:
            return ConstantExpression(Constants.ZERO)

    def e_step(self):
        """
        E(C) = 0
        """

        return Constants.ZERO

    def simplify(self):

        return self
