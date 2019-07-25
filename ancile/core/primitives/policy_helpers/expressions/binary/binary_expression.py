from abc import ABC

from ancile.core.primitives.policy_helpers.expressions.base_expression import BaseExpression


class BinaryExpression(BaseExpression, ABC):

    def __init__(self, command1, command2):
        super().__init__()
        self.command1 = command1
        self.command2 = command2

    def __repr__(self):
        return f'{self.command1} {self.operation} {self.command2}'

