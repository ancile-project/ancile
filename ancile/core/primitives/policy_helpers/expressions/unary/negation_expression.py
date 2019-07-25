from ancile.core.primitives import Policy
from ancile.core.primitives.policy_helpers.expressions.base_expression import BaseExpression
from ancile.core.primitives.policy_helpers.expressions.exec_expression import ExecExpression
from ancile.core.primitives.policy_helpers.expressions.unary.unary_expression import UnaryExpression


class NegationExpression(UnaryExpression):

    def __init__(self, expression: BaseExpression):
        super().__init__(expression)

    def __repr__(self):
        if isinstance(self.expression, ExecExpression):
            return f'!{self.expression}'
        else:
            return f'!({self.expression})'

    def d_step(self):
        pass

    def e_step(self):
        pass

    def simplify(self):
        pass
