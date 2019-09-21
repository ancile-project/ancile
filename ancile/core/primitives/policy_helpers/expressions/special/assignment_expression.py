from ancile.core.primitives import Command
from ancile.core.primitives.policy_helpers.expressions import BaseExpression, Constants, ConstantExpression
from ancile.core.primitives.policy_helpers.expressions.special.tests import Test


class AssignmentExpression(BaseExpression):

    def __init__(self, name):

        self.name = name
        # self.test.val = val


    def d_step(self, command: Command) -> BaseExpression:
        return ConstantExpression(Constants.ZERO)

    def e_step(self) -> Constants:
        return Constants.ZERO

    def simplify(self) -> BaseExpression:
        return ConstantExpression(Constants.ZERO)
