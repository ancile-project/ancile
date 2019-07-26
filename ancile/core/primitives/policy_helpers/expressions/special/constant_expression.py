from ancile.core.primitives.policy_helpers.expressions import *


class ConstantExpression(BaseExpression):
    command: Constants

    def __init__(self, command: Constants):
        super().__init__()

        self.command = command

    def __repr__(self):
        return f'{self.command}'

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.command == other.command:
            return True
        else:
            return False

    def d_step(self, command, params=None) -> BaseExpression:
        """
        D(0, C) = 0
        D(1, C) = 0

        """

        return ConstantExpression(Constants.ZERO)

    def e_step(self) -> Constants:
        """
        E(0) = 0
        E(1) = 1

        :return:
        """
        return self.command

    def simplify(self):

        return self
