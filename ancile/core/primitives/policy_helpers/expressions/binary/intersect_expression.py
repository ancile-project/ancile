from abc import ABC
from ancile.core.primitives.policy_helpers.expressions import *


class IntersectExpression(BinaryExpression):

    def __init__(self, l_expr: BaseExpression, r_expr: BaseExpression):
        self.operation = '&'
        super().__init__(l_expr, r_expr)

    def __eq__(self, other):
        """
        P1 & P2 = P2 & P1
        :param other:
        :return:
        """
        if isinstance(other, self.__class__):
            if self.l_expr == other.l_expr and self.r_expr == other.r_expr \
                    or self.l_expr == other.r_expr and self.l_expr == other.r_expr:
                return True
        else:
            return False

    def d_step(self, command):
        """
        D(P1 & P2, C) = D(P1, C) & D(P2, C)

        """
        self.l_expr = self.l_expr.simplify()
        self.r_expr = self.r_expr.simplify()

        return IntersectExpression(self.l_expr.d_step(command),
                                   self.r_expr.d_step(command)).simplify()

    def e_step(self):
        """
        E(P1 & P2, C) = E(P1) AND E(P2)
        :return:
        """

        return self.l_expr.e_step() * self.r_expr.e_step()

    def simplify(self):
        """
        P + P = P
        P & 0 = 0 + P = P
        P* + 1 = P*

        """
        self.l_expr = self.l_expr.simplify()
        self.r_expr = self.r_expr.simplify()

        if self.l_expr == self.r_expr:
            return self.l_expr
        elif self.l_expr == ConstantExpression(Constants.ZERO) or self.r_expr == ConstantExpression(Constants.ZERO):
            return ConstantExpression(Constants.ZERO)
        elif self.l_expr == ConstantExpression(Constants.ONE) and isinstance(self.r_expr, StarExpression):
            return self.r_expr
        elif self.r_expr == ConstantExpression(Constants.ONE) and isinstance(self.l_expr, StarExpression):
            return self.l_expr
        else:
            return self
