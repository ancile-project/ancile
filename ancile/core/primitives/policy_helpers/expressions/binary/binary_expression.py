from abc import ABC
from ancile.core.primitives.policy_helpers.expressions import *


class BinaryExpression(BaseExpression, ABC):
    l_expr: BaseExpression
    r_expr: BaseExpression

    def __init__(self, l_expr, r_expr):
        super().__init__()
        self.l_expr = l_expr
        self.r_expr = r_expr

    def __repr__(self):
        if isinstance(self.l_expr, ExecExpression) and isinstance(self.r_expr, ExecExpression):
            return f'{self.l_expr}{self.operation}{self.r_expr}'
        elif isinstance(self.l_expr, ExecExpression):
            return f'{self.l_expr}{self.operation}({self.r_expr})'
        elif isinstance(self.r_expr, ExecExpression):
            return f'({self.l_expr}){self.operation}{self.r_expr}'
        else:
            return f'({self.l_expr}){self.operation}({self.r_expr})'
