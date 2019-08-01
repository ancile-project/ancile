from ancile.core.primitives.policy_helpers.expressions import *


class ConcatExpression(BinaryExpression):

    def __init__(self, l_expr: BaseExpression, r_expr: BaseExpression):
        self.operation = '.'
        super().__init__(l_expr, r_expr)

    def __eq__(self, other):
        """
        Only strict equality as position matters.
        """
        if isinstance(other, self.__class__):
            if self.l_expr == other.l_expr and self.r_expr == other.r_expr:
                return True
        else:
            return False

    def d_step(self, command):
        """
        D(P1.P2, C) = D(P1,C).P2 + E(P1).D(P2,C)
        """
        self.l_expr = self.l_expr.simplify()
        self.r_expr = self.r_expr.simplify()

        new_l_expr = ConcatExpression(self.l_expr.d_step(command),
                                      self.r_expr)
        new_r_expr = ConcatExpression(ConstantExpression(self.l_expr.e_step()),
                                      self.r_expr.d_step(command))

        return UnionExpression(new_l_expr, new_r_expr).simplify()

    def e_step(self):
        """
        E(P1.P2) = E(P1) * E(P2)
        :return:
        """

        return self.l_expr.e_step() * self.r_expr.e_step()

    def simplify(self):
        """
        P.1 = 1.P = P
        0.P = P.0 = 0

        """
        self.l_expr = self.l_expr.simplify()
        self.r_expr = self.r_expr.simplify()

        if self.l_expr == ConstantExpression(Constants.ONE):
            return self.r_expr
        elif self.r_expr == ConstantExpression(Constants.ONE):
            return self.l_expr
        elif self.l_expr == ConstantExpression(Constants.ZERO) \
                or self.r_expr == ConstantExpression(Constants.ZERO):
            return ConstantExpression(Constants.ZERO)
        else:
            return self


