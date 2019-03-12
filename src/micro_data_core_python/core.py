from src.micro_data_core_python.policy_sly import PolicyParser
import src.micro_data_core_python.policy_processor as decorator
from src.micro_data_core_python.functions import *



def execute(program, policy, sensitive_data=None):

    parsed_policy = PolicyParser.parse_it(policy.decode('ascii'))
    decorator.PolicyProcessor.current_policy = parsed_policy
    print(f'\nparsed policy: {decorator.PolicyProcessor.current_policy}')
    program = program.decode('ascii')
    print(f'submitted program:\n{program}\n')
    data = []
    try:
        exec(program)
    except ValueError:
        return False
    return data


if __name__ == '__main__':

    res = execute(b'data.append(5)\nasdf()\nqwer()', b'asdf.qwer', None)
    print(f'POLICY EVALUATED TO {res}\n')
    res = execute(b'data.append(5)\nqwer()\nqwer()', b'qwer.asdf', None)
    print(f'POLICY EVALUATED TO {res}')

