from ancile.core.primitives.policy_helpers.expressions import *


class ConcatExpression(BinaryExpression):

    def __init__(self, l_expr: BaseExpression, r_expr: BaseExpression):
        self.operation = '.'
        super().__init__(l_expr, r_expr)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.l_expr == other.l_expr and self.r_expr == other.r_expr:
                return True
        else:
            return False

    def d_step(self, command, params=None):

        pass

    def e_step(self):
        pass

    def simplify(self):
        pass


