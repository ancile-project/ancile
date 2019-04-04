from src.micro_data_core_python.errors import AncileException


class DataPolicyPair:

    def __init__(self, policy, token, name, username, private_data):
        self._name = name
        self._username = username
        self._data = {}
        self._policy = policy
        self._token = token
        self._private_data = private_data

    def _call_transform(self, func, *args, **kwargs):
        check_is_func(func)
        command = func.__name__
        print(f'old policy: {self._policy}.')
        self._policy = DataPolicyPair.d_step(self._policy, command)
        print(f'new policy: {self._policy}, data: {self._data}')
        if self._policy:
            # replace in kwargs:
            kwargs['data'] = self._data
            return func(*args, **kwargs)
        else:
            raise ValueError('Policy prevented from running')

    def _call_fetch(self, func, *args, **kwargs):
        check_is_func(func)
        command = func.__name__
        print(f'old policy: {self._policy}.')
        self._policy = DataPolicyPair.d_step(self._policy, command)
        print(f'new policy: {self._policy}, data: {self._data}')
        if self._policy:
            kwargs['data'] = self._data
            kwargs['token'] = self._token
            return func(*args, **kwargs)
        else:
            raise ValueError('Policy prevented from running')

    def _use_method(self, func, *args, **kwargs):
        print(f'return policy: {self._policy}, data: {self._data}')
        check_is_func(func)
        self._policy = self.d_step(self._policy, func.__name__)
        step_result = DataPolicyPair.e_step(self._policy)
        if step_result == 1:
            kwargs['data'] = self._data
            return func(*args, **kwargs)
        else:
            raise ValueError(f'Last E step failed: {self._policy}')

    @staticmethod
    def d_step(policy, command):
        if policy in [0, 1]:
            return policy

        operator = policy[0]
        if operator == 'exec':
            if policy[1] == command:
                return 1
            elif policy[1] == 'ANYF':
                return 1
            else:
                return 0
        elif operator == 'concat':
            p1 = DataPolicyPair.simplify(['concat', DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command)), policy[2]])
            p2 = DataPolicyPair.simplify(['concat', DataPolicyPair.e_step(policy[1]), DataPolicyPair.simplify(DataPolicyPair.d_step(policy[2], command))])
            return DataPolicyPair.simplify(['union', p1, p2])
        elif operator == 'union':
            p1 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command))
            p2 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[2], command))
            return DataPolicyPair.simplify(['union', p1, p2])
        elif operator == 'star':
            p1 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command))
            p2 = ['star', policy[1]]
            return DataPolicyPair.simplify(['concat', p1, p2])
        elif operator == 'intersect':
            p1 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command))
            p2 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[2], command))
            return DataPolicyPair.simplify(['intersect', p1, p2])
        elif operator == 'neg':
            return ['neg', DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command))]
        else:
            raise ValueError(f'Cannot process following policy: {policy}.')

    @staticmethod
    def simplify(policy):
        if policy in [0, 1]:
            return policy

        operator = policy[0]

        if operator == 'exec':
            return policy
        elif operator in ['star', 'neg']:
            return [operator, DataPolicyPair.simplify(policy[1])]
        elif operator in ['concat', 'union', 'intersect']:
            if policy[0] == policy[1]:
                return policy[0]

            elif operator in ['concat', 'intersect']:
                if policy[1] == 0:
                    return 0
                elif policy[2] == 0:
                    return 0
                elif policy[1] == 1:
                    return DataPolicyPair.simplify(policy[2])
                elif policy[2] == 1:
                    return DataPolicyPair.simplify(policy[1])

            elif operator == 'union':
                if policy[1] == 0:
                    return DataPolicyPair.simplify(policy[2])
                elif policy[2] == 0:
                    return DataPolicyPair.simplify(policy[1])
                elif policy[1] == 1:
                    return 1
                elif policy[2] == 1:
                    return 1

            elif operator in ['intersect', 'union']:
                if policy[1][0] == policy[2][0] and policy[1][0] in ['intersect', 'union']:
                    if policy[1][1] == policy[2][2] and policy[1][2] == policy[2][1]:
                        return DataPolicyPair.simplify(policy[1])

            return [operator, DataPolicyPair.simplify(policy[1]), DataPolicyPair.simplify(policy[2])]

        else:
            return policy

    @staticmethod
    def e_step(policy):
        if policy in [0, 1]:
            return policy

        operator = policy[0]
        if operator == 'exec':
            return 0
        elif operator == 'concat':
            return DataPolicyPair.e_step(policy[1]) * DataPolicyPair.e_step(policy[2])
        elif operator == 'intersect':
            return DataPolicyPair.e_step(policy[1]) * DataPolicyPair.e_step(policy[2])
        elif operator == 'union':
            return max(DataPolicyPair.e_step(policy[1]), DataPolicyPair.e_step(policy[2]))
        elif operator == 'star':
            return 1
        elif operator == 'neg':
            return abs(DataPolicyPair.e_step(policy[1]) - 1)
        else:
            raise ValueError(f'Incorrect e_step, input: {policy}.')


def check_is_func(func):
    if not callable(func):
        raise AncileException("You can't call operation on the DataPair object. Use only allowed functions.")
