from copy import deepcopy
from ancile_core.policy_sly import PolicyParser
# from typing import List


class Policy(object):
    def __init__(self, initial_policy):
        if isinstance(initial_policy, str):
            self._policy = PolicyParser.parse_it(initial_policy)
        elif isinstance(initial_policy, Policy):
            self._policy = deepcopy(initial_policy._policy)
        else:
            self._policy = deepcopy(initial_policy)

    def d_step(self, command, scope=None, in_place=False):
        if not in_place:
            return Policy(Policy._d_step(self._policy, command, scope))
        else:
            self._policy = Policy._d_step(self._policy, command, scope)
            return self

    def e_step(self) -> int:
        return Policy._e_step(self._policy)

    def __bool__(self):
        return self._policy != 0

    def check_allowed(self, command, kwargs=None):
        return bool(self.d_step({'command': command, 'kwargs': kwargs}))

    def __repr__(self):
        return f'<? POLICY : {self._policy} ?>'

    @staticmethod
    def _d_step(policy, command, scope=None):
        """


        :param policy: current policy
        :param command:
        :param scope: a high-level scope of functions (transform, fetch, etc). If scope specified then we check the
        policy against it as well.

        :return:
        """
        # policy = policy._policy if isinstance(policy, Policy) else policy

        if policy in [0, 1]:
            return 0

        operator = policy[0]
        if operator == 'exec':
            if policy[1] == command['command']:
                # add params check:
                if len(policy) > 2 and policy[2]:
                    policy_kwargs = policy[2]
                    kwargs = command['kwargs']
                    for key, value in policy_kwargs.items():
                        if key == 'data':
                            continue
                        # print(f'Checking for key: {key} and value: {value}, passed param: {kwargs.get(key, False)}\n')
                        proposed_value = kwargs.get(key, None)

                        if not value.evaluate(proposed_value):
                            return 0

                return 1
            elif policy[1] == 'ANYF':
                return 1
            elif policy[1] == scope:
                return 1
            else:
                return 0
        elif operator == 'concat':
            p1 = Policy._simplify(['concat',
                            Policy._simplify(Policy._d_step(policy[1], command, scope)),
                            policy[2]])
            p2 = Policy._simplify(['concat', Policy._e_step(policy[1]),
                            Policy._simplify(Policy._d_step(policy[2], command, scope))])
            return Policy._simplify(['union', p1, p2])
        elif operator == 'union':
            p1 = Policy._simplify(Policy._d_step(policy[1], command, scope))
            p2 = Policy._simplify(Policy._d_step(policy[2], command, scope))
            return Policy._simplify(['union', p1, p2])
        elif operator == 'star':
            p1 = Policy._simplify(Policy._d_step(policy[1], command, scope))
            p2 = ['star', policy[1]]
            return Policy._simplify(['concat', p1, p2])
        elif operator == 'intersect':
            p1 = Policy._simplify(Policy._d_step(policy[1], command, scope))
            p2 = Policy._simplify(Policy._d_step(policy[2], command, scope))
            return Policy._simplify(['intersect', p1, p2])
        elif operator == 'neg':
            return ['neg', Policy._simplify(Policy._d_step(policy[1], command, scope))]
        else:
            error = f'Cannot process following policy: {policy}.'
            raise ValueError(error)

    @staticmethod
    def _simplify(policy):
        if policy in [0, 1]:
            return policy

        operator = policy[0]

        if operator == 'exec':
            return policy
        elif operator in ['star', 'neg']:
            return [operator, Policy._simplify(policy[1])]
        elif operator in ['concat', 'union', 'intersect']:
            if policy[0] == policy[1]:
                return policy[0]

            elif operator=='concat':
                if policy[1] == 0:
                    return 0
                elif policy[2] == 0:
                    return 0
                elif policy[1] == 1:
                    return Policy._simplify(policy[2])
                elif policy[2] == 1:
                    return Policy._simplify(policy[1])

            elif operator == 'intersect':
                if policy[1] == 0:
                    return 0
                elif policy[2] == 0:
                    return 0
                elif policy[1] == 1 and policy[2][0]=='star':
                    return 1
                elif policy[2] == 1 and policy[1][0]=='star':
                    return 1

            elif operator == 'union':
                if policy[1] == 0:
                    return Policy._simplify(policy[2])
                elif policy[2] == 0:
                    return Policy._simplify(policy[1])
                elif policy[1] == 1 and policy[2][0]=='star':
                    return Policy._simplify(policy[2])
                elif policy[2] == 1 and policy[1][0]=='star':
                    return Policy._simplify(policy[1])

            elif operator in ['intersect', 'union']:
                if policy[1][0] == policy[2][0] and                           \
                   policy[1][0] in ['intersect', 'union']:
                    if policy[1][1] == policy[2][2] and                       \
                       policy[1][2] == policy[2][1]:
                        return Policy._simplify(policy[1])

            return [operator, Policy._simplify(policy[1]),
                    Policy._simplify(policy[2])]

        else:
            return policy

    @staticmethod
    def _e_step(policy):
        # policy = policy._policy if isinstance(policy, Policy) else policy

        if policy in [0, 1]:
            return policy

        operator = policy[0]
        if operator == 'exec':
            return 0
        elif operator == 'concat':
            return Policy._e_step(policy[1]) * Policy._e_step(policy[2])
        elif operator == 'intersect':
            return Policy._e_step(policy[1]) * Policy._e_step(policy[2])
        elif operator == 'union':
            return max(Policy._e_step(policy[1]), Policy._e_step(policy[2]))
        elif operator == 'star':
            return 1
        elif operator == 'neg':
            return abs(Policy._e_step(policy[1]) - 1)
        else:
            error = f'Incorrect e_step, input: {policy}.'
            raise ValueError(error)


def concat(p1: Policy, p2: Policy) -> Policy:
    return Policy(['concat', p1._policy, p2._policy])

def intersect(p1: Policy, p2: Policy) -> Policy:
    return Policy(['intersect', p1._policy, p2._policy])

def union(p1: Policy, p2: Policy) -> Policy:
    return Policy(['union', p1._policy, p2._policy])
