from ancile.core.primitives import Policy
from ancile.core.primitives.policy_helpers.expressions.base_expression import BaseExpression


class ExecExpression(BaseExpression):

    def __init__(self, command: str, params=None):
        super().__init__()
        self.command = command
        self.params = params

    def __repr__(self):
        if self.params:
            return f'{self.command}({", ".join([str(x) for x in self.params])})'
        else:
            return f'{self.command}'

    def __eq__(self, other):
        if type(self) is type(other) and self.command == other.command \
                and self.params == other.params:
            return True
        else:
            return False

    def d_step(self):
        pass

    def e_step(self):
        pass

    def simplify(self):
        pass
