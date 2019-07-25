from abc import ABC

from ancile.core.primitives.policy_helpers.expressions.base_expression import BaseExpression


class UnaryExpression(BaseExpression, ABC):

    def __init__(self, expression: BaseExpression):
        super().__init__()
        self.expression = expression

    def __eq__(self, other):
        if type(self) is type(other) and self.expression == other.expression:
            return True

    def d_step(self):
        pass

    def e_step(self):
        pass

    def simplify(self):
        pass
