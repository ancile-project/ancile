from ancile.core.primitives.policy_helpers.expressions import *


class StarExpression(UnaryExpression):

    def __init__(self, expression: BaseExpression):
        self.operation = '*'
        super().__init__(expression)

    def __repr__(self):
        if type(self.expression) in [ConstantExpression, ActionExpression]:
            return f'{self.expression}*'
        else:
            return f'({self.expression})*'

    def d_step(self, command, atoms):
        """
        D(P*) = D(P,C).P*
        :param atoms:

        """
        self.expression = self.expression.simplify()

        return ConcatExpression(self.expression.d_step(command, atoms), self).simplify()

    def e_step(self, atoms):
        """
        E(P*) = 1
        :param atoms:
        """

        return Constants.ONE

    def simplify(self):
        return StarExpression(self.expression.simplify())
