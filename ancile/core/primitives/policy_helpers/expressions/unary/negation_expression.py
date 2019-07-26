from ancile.core.primitives.policy_helpers.expressions import *


class NegationExpression(UnaryExpression):

    def __init__(self, expression: BaseExpression):
        self.operation = '!'
        super().__init__(expression)

    def __repr__(self):
        if isinstance(self.expression, ExecExpression):
            return f'!{self.expression}'
        else:
            return f'!({self.expression})'

    def d_step(self, command, params=None):
        """
        D(!P) = !D(P,C)
        """

        return self.__class__(self.expression.d_step(command, params))

    def e_step(self):
        pass

    def simplify(self):
        pass
