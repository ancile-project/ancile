from abc import ABC

from ancile.core.primitives.policy_helpers.expressions.base_expression import BaseExpression


class UnaryExpression(BaseExpression, ABC):

    def __init__(self, expression: BaseExpression):
        super().__init__()
        self.expression = expression

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.expression == other.expression:
            return True

    def d_step(self):
        pass

    def e_step(self):
        pass

    def simplify(self):
        pass
