from abc import ABC

from ancile.core.primitives.policy_helpers.expressions.base_expression import BaseExpression
from ancile.core.primitives.policy_helpers.expressions.binary.binary_expression import BinaryExpression


class UnionExpression(BinaryExpression):

    def __init__(self, l_expr: BaseExpression, r_expr: BaseExpression):
        self.operation = '/\\'
        super().__init__(l_expr, r_expr)

    def d_step(self):
        pass

    def e_step(self):
        pass

    def simplify(self):
        pass


