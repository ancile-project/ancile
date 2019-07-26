from ancile.core.primitives.policy_helpers.expressions import *
from ancile.core.primitives.policy_helpers.expressions.noop_expression import NoOpExpression


class ExecExpression(BaseExpression):

    def __init__(self, command: str, params=None):
        super().__init__()
        self.command = command
        self.params = params

    def __repr__(self):
        if self.params:
            return f'{self.command}({", ".join([str(x) for x in self.params.values()])})'
        else:
            return f'{self.command}'

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.command == other.command \
                and self.params == other.params:
            return True
        else:
            return False

    def d_step(self, command, params=None):
        if self.command == command:
            for key, value in self.params.items():
                if key == 'data':
                    continue
                # print(f'Checking for key: {key} and value: {value}, passed param: {params.get(key, False)}\n')
                proposed_value = params.get(key, None)
                if not value.evaluate(proposed_value):
                    return Constants.ZERO

            return Constants.ONE

    def e_step(self):
        """
        E(C) = 0
        :return:
        """

        return Constants.ZERO

    def simplify(self):

        return self
