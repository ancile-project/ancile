import wrapt
from src.micro_data_core_python.policy_sly import PolicyParser

from src.micro_data_core_python.functions import *

class Core:

    def __init__(self, program, policy, sensitive_data=None):
        self.program = program
        self.policy = PolicyParser.parse_it(policy)

        self.sensitive_data = sensitive_data


    def execute(self):
        import src.micro_data_core_python.policy_processor as decorator
        print(f'previous policy: {decorator.PolicyProcessor.current_policy}')
        decorator.PolicyProcessor.current_policy = self.policy
        print(f'New policy: {decorator.PolicyProcessor.current_policy}')
        exec(self.program)


if __name__ == '__main__':
    print('a')
    # c = Core('asdf()\nqwer()', 'asdf.qwer', None)
    # c.execute()
    c = Core('qwer()\nqwer()', 'qwer.asdf', None)
    c.execute()

