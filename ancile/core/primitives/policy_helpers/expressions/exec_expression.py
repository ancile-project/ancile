from ancile.core.primitives import Policy
from ancile.core.primitives.policy_helpers.command import Command
from ancile.core.primitives.policy_helpers.expressions.base_expression import BaseExpression


class ExecExpression(BaseExpression):

    def __init__(self, command: Command):
        super().__init__()
        self.command = command

    def __repr__(self):
        return self.command

    def d_step(self):
        pass

    def e_step(self):
        pass

    def simplify(self):
        pass