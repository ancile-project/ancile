from abc import ABC
from ancile.core.primitives.policy_helpers.expressions import *


class UnaryExpression(BaseExpression, ABC):
    expression: BaseExpression

    def __init__(self, expression: BaseExpression):
        super().__init__()
        self.expression = expression

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.expression == other.expression:
            return True
