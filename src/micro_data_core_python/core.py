from src.micro_data_core_python.policy_sly import PolicyParser
from src.micro_data_core_python.functions import *


def execute(policies, program, sensitive_data=None):
    parsed_policies = dict()
    for provider, policy in policies.items():
        parsed_policies[provider] = PolicyParser.parse_it(policy.decode('ascii'))

    UserSpecific._user_policies = parsed_policies
    print(f'\nparsed policies: {UserSpecific._user_policies}')
    program = program.decode('ascii')
    print(f'submitted program:\n{program}\n')
    result = []
    exec(program)

    return result


if __name__ == '__main__':
    res = execute({'dataA': b'fetch_test_data.asdf.qwer.return_data'},
b'''
data_pair=fetch_test_data(data_source="dataA")
asdf(data=data_pair)
qwer(data=data_pair)
result.append(return_data(data=data_pair))
''',
                  None)
    print(f'POLICY EVALUATED TO {res}\n')

