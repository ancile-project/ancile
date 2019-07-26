from ancile.core.primitives.policy_helpers.expressions import *


class StarExpression(UnaryExpression):

    def __init__(self, expression: BaseExpression):
        self.operation = '*'
        super().__init__(expression)

    def __repr__(self):
        if isinstance(self.expression, ExecExpression):
            return f'{self.expression}*'
        else:
            return f'({self.expression})*'

    def d_step(self, command, params=None):
        """
        D(P*) = D(P,C).P*

        """
        self.expression = self.expression.simplify()

        return ConcatExpression(self.expression.d_step(command, params), self)

    def e_step(self):
        """
        E(P*) = 1
        """

        return Constants.ONE

    def simplify(self):
        pass
