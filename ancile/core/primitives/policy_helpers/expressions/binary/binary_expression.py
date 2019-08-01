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
        if type(self.l_expr) in [ConstantExpression, ExecExpression] \
                and type(self.r_expr) in [ConstantExpression, ExecExpression]:
            return f'{self.l_expr}{self.operation}{self.r_expr}'
        elif type(self.l_expr) in [ConstantExpression, ExecExpression]:
            return f'{self.l_expr}{self.operation}({self.r_expr})'
        elif type(self.r_expr) in [ConstantExpression, ExecExpression]:
            return f'({self.l_expr}){self.operation}{self.r_expr}'
        else:
            return f'({self.l_expr}){self.operation}({self.r_expr})'

    @classmethod
    def assemble_from_list(cls, expressions,
                           empty_expr=ConstantExpression(Constants.ZERO)):
        """Combines a passed list of expressions as a tree of
        individual expression

        """

        expr_box = iter(expressions)

        l_expr = next(expr_box, None)
        if l_expr is None:
            return empty_expr

        r_expr = next(expr_box, None)
        if r_expr is None:
            return l_expr

        assembled_expr = cls(l_expr, r_expr)
        for expr in expr_box:
            assembled_expr = cls(assembled_expr, expr)

        return assembled_expr
