from ancile.core.primitives.policy_helpers.expressions import *


class NegationExpression(UnaryExpression):

    def __init__(self, expression: BaseExpression):
        self.operation = '!'
        super().__init__(expression)

    def __repr__(self):
        if type(self.expression) in [ConstantExpression, ActionExpression] :
            return f'!{self.expression}'
        else:
            return f'!({self.expression})'

    def d_step(self, command, atoms) -> BaseExpression:
        """
        D(!P) = !D(P,C)
        :param atoms:
        """
        self.expression = self.expression.simplify()

        return NegationExpression(self.expression.d_step(command, atoms))

    def e_step(self, atoms) -> Constants:
        """
        E(!P) = !E(P)

        negation sign is responsible to invert value
        :param atoms:
        """

        return -self.expression.e_step(atoms)

    def simplify(self):
        return NegationExpression(self.expression.simplify())
