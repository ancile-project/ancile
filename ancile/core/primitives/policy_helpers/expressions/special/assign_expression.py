from ancile.core.primitives.policy_helpers.expressions import *
from copy import deepcopy

class AssignExpression(BaseExpression):
    command: Constants

    def __init__(self, name):
        super().__init__()

        self.name = name
        self.val = Constants.ZERO

    def __repr__(self):
        return f'{self.name}!'

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.command == other.command:
            return True
        else:
            return False

    def d_step(self, command, atoms) -> BaseExpression:
        """
        D(0, C) = 0
        D(1, C) = 0
        :param atoms:

        """
        atoms[self.name] = not atoms.get(self.name, False)

        return ConstantExpression(Constants.ONE)

    def e_step(self, atoms) -> Constants:
        """
        E(0) = 0
        E(1) = 1

        :param atoms:
        :return:
        """

        return Constants.ONE

    def simplify(self):

        return self
