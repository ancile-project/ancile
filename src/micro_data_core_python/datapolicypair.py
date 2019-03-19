# from src.micro_data_core_python.functions import *

class DataPolicyPair:

    def __init__(self, policy):
        self._data = {}
        self._policy = policy

    def call(self, func, *args, **kwargs):
        if not callable(func):
            return NameError
        command = func.__name__
        if func.__name__ == 'return_data':
            DataPolicyPair.e_step(self._policy)
            return self._data
        else:
            self._policy = DataPolicyPair.d_step(self._policy, command)
            print(f'new policy: {self._policy}, data: {self._data}')
            if self._policy:
                # replace in kwargs:
                kwargs['data'] = self._data

                return func(*args, **kwargs)
            else:
                raise ValueError('Policy prevented from running')

    def return_data(self, func, *args, **kwargs):
        print(f'return policy: {self._policy}, data: {self._data}')
        if not callable(func) or func.__name__ != 'return_data':
            return NameError

        if DataPolicyPair.e_step(self.d_step(self._policy, func.__name__)):
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
