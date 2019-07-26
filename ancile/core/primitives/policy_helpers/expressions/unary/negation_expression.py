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

    def d_step(self, command, params=None) -> BaseExpression:
        """
        D(!P) = !D(P,C)
        """
        self.expression = self.expression.simplify()

        return NegationExpression(self.expression.d_step(command, params))

    def e_step(self) -> Constants:
        """
        E(!P) = !E(P)

        negation sign is responsible to invert value
        """

        return -self.expression.e_step()

    def simplify(self):
        pass
