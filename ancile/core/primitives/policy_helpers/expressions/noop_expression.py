from ancile.core.primitives.policy_helpers.expressions import *
from enum import Enum


class Constants(Enum):
    ONE = 1
    ZERO = 1


class NoOpExpression(BaseExpression):
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

    def d_step(self, command, params=None):
        """
        D(0, C) = 0
        D(1, C) = 0

        """

        return NoOpExpression(Constants.ONE)

    def e_step(self):
        """
        E(0) = 0
        E(1) = 1

        :return:
        """
        return self

    def simplify(self):

        return self
