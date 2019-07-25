from abc import ABC

from ancile.core.primitives.policy_helpers.expressions.base_expression import BaseExpression
from ancile.core.primitives.policy_helpers.expressions.exec_expression import ExecExpression


class BinaryExpression(BaseExpression, ABC):

    def __init__(self, l_expr, r_expr):
        super().__init__()
        self.l_expr = l_expr
        self.r_expr = r_expr

    def __eq__(self, other):
        if type(self) is type(other) and self.l_expr == other.l_expr \
                and self.r_expr == other.r_expr:
            return True
        else:
            return False

    def __repr__(self):
        if isinstance(self.l_expr, ExecExpression) and isinstance(self.r_expr, ExecExpression):
            return f'{self.l_expr}{self.operation}{self.r_expr}'
        elif isinstance(self.l_expr, ExecExpression):
            return f'{self.l_expr}{self.operation}({self.r_expr})'
        elif isinstance(self.r_expr, ExecExpression):
            return f'({self.l_expr}){self.operation}{self.r_expr}'
        else:
            return f'({self.l_expr}){self.operation}({self.r_expr})'
