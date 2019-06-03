from copy import deepcopy
# from typing import List


class Policy(object):
    def __init__(self, initial_policy):
        self._policy = deepcopy(initial_policy)

    def d_step(self, command, scope=None, in_place=False):
        if not in_place:
            return Policy(_d_step(self._policy, command, scope))
        else:
            self._policy = _d_step(self._policy, command, scope)
            return self

    def e_step(self) -> int:
        return _e_step(self._policy)

    def __bool__(self):
        return self._policy != 0


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
        return policy

    operator = policy[0]
    if operator == 'exec':
        if policy[1] == command['command']:
            # add params check:
            if len(policy) > 2 and policy[2]:
                policy_kwargs = policy[2]
                kwargs = command['kwargs']
                for key, value in policy_kwargs.items():
                    print(f'Checking for key: {key} and value: {value}, passed param: {kwargs.get(key, False)}')
                    if key != 'data' and value != kwargs.get(key, False):
                        return 0
            return 1
        elif policy[1] == 'ANYF':
            return 1
        elif policy[1] == scope:
            return 1
        else:
            return 0
    elif operator == 'concat':
        p1 = _simplify(['concat',
                        _simplify(_d_step(policy[1], command, scope)),
                        policy[2]])
        p2 = _simplify(['concat', _e_step(policy[1]),
                        _simplify(_d_step(policy[2], command, scope))])
        return _simplify(['union', p1, p2])
    elif operator == 'union':
        p1 = _simplify(_d_step(policy[1], command, scope))
        p2 = _simplify(_d_step(policy[2], command, scope))
        return _simplify(['union', p1, p2])
    elif operator == 'star':
        p1 = _simplify(_d_step(policy[1], command, scope))
        p2 = ['star', policy[1]]
        return _simplify(['concat', p1, p2])
    elif operator == 'intersect':
        p1 = _simplify(_d_step(policy[1], command, scope))
        p2 = _simplify(_d_step(policy[2], command, scope))
        return _simplify(['intersect', p1, p2])
    elif operator == 'neg':
        return ['neg', _simplify(_d_step(policy[1], command, scope))]
    else:
        error = f'Cannot process following policy: {policy}.'
        raise ValueError(error)


def _simplify(policy):
    if policy in [0, 1]:
        return policy

    operator = policy[0]

    if operator == 'exec':
        return policy
    elif operator in ['star', 'neg']:
        return [operator, _simplify(policy[1])]
    elif operator in ['concat', 'union', 'intersect']:
        if policy[0] == policy[1]:
            return policy[0]

        elif operator in ['concat', 'intersect']:
            if policy[1] == 0:
                return 0
            elif policy[2] == 0:
                return 0
            elif policy[1] == 1:
                return _simplify(policy[2])
            elif policy[2] == 1:
                return _simplify(policy[1])

        elif operator == 'union':
            if policy[1] == 0:
                return _simplify(policy[2])
            elif policy[2] == 0:
                return _simplify(policy[1])
            elif policy[1] == 1:
                return 1
            elif policy[2] == 1:
                return 1

        elif operator in ['intersect', 'union']:
            if policy[1][0] == policy[2][0] and                               \
               policy[1][0] in ['intersect', 'union']:
                if policy[1][1] == policy[2][2] and                           \
                   policy[1][2] == policy[2][1]:
                    return _simplify(policy[1])

        return [operator, _simplify(policy[1]), _simplify(policy[2])]

    else:
        return policy


def _e_step(policy):
    # policy = policy._policy if isinstance(policy, Policy) else policy

    if policy in [0, 1]:
        return policy

    operator = policy[0]
    if operator == 'exec':
        return 0
    elif operator == 'concat':
        return _e_step(policy[1]) * _e_step(policy[2])
    elif operator == 'intersect':
        return _e_step(policy[1]) * _e_step(policy[2])
    elif operator == 'union':
        return max(_e_step(policy[1]), _e_step(policy[2]))
    elif operator == 'star':
        return 1
    elif operator == 'neg':
        return abs(_e_step(policy[1]) - 1)
    else:
        error = f'Incorrect e_step, input: {policy}.'
        raise ValueError(error)


def concat(p1: Policy, p2: Policy) -> Policy:
    return Policy(['concat', p1._policy, p2._policy])

def intersect(p1: Policy, p2: Policy) -> Policy:
    return Policy(['intersect', p1._policy, p2._policy])

def union(p1: Policy, p2: Policy) -> Policy:
    return Policy(['union', p1._policy, p2._policy])
