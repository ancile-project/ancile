class PolicyProcessor:
    current_policy = []

    @classmethod
    def decorator(cls, f):
        def wrapper(*args, **kwargs):
            print('decorator')
            print(f.__name__)
            print(f'executing command: {f.__name__} over policy: {cls.current_policy}')
            cls.current_policy = d_step(cls.current_policy, f.__name__)
            print(f'd step output: {cls.current_policy}')
            if cls.current_policy:
                return f(*args, **kwargs)
            else:
                raise ValueError(f"The policy prevented from running this function: {f.__name__}. Abort.")

        return wrapper


def d_step(policy, command):
    if policy in [0, 1]:
        return policy

    operator = policy[0]
    if operator == 'exec':
        if policy[1] == command:
            return 1
        else:
            return 0
    elif operator == 'concat':
        p1 = simplify(['concat', simplify(d_step(policy[1], command)), policy[2]])
        p2 = simplify(['concat', e_step(policy[1]), simplify(d_step(policy[2], command))])
        return simplify(['union', p1, p2])
    elif operator == 'union':
        p1 = simplify(d_step(policy[1], command))
        p2 = simplify(d_step(policy[2], command))
        return simplify(['union', p1, p2])
    elif operator == 'star':
        p1 = simplify(d_step(policy[1], command))
        p2 = ['star', policy[1]]
        return simplify(['concat', p1, p2])
    elif operator == 'intersect':
        p1 = simplify(d_step(policy[1], command))
        p2 = simplify(d_step(policy[2], command))
        return simplify(['intersect', p1, p2])
    elif operator == 'neg':
        return ['neg', simplify(d_step(policy[1], command))]
    else:
        raise ValueError(f'Cannot process following policy: {policy}.')


def simplify(policy):
    if policy in [0, 1]:
        return policy

    operator = policy[0]

    if operator == 'exec':
        return policy
    elif operator in ['star', 'neg']:
        return [operator, simplify(policy[1])]
    elif operator in ['concat', 'union', 'intersect']:
        if policy[0] == policy[1]:
            return policy[0]

        elif operator in ['concat', 'intersect']:
            if policy[1] == 0:
                return 0
            elif policy[2] == 0:
                return 0
            elif policy[1] == 1:
                return simplify(policy[2])
            elif policy[2] == 1:
                return simplify(policy[1])

        elif operator == 'union':
            if policy[1] == 0:
                return simplify(policy[2])
            elif policy[2] == 0:
                return simplify(policy[1])
            elif policy[1] == 1:
                return 1
            elif policy[2] == 1:
                return 1

        elif operator in ['intersect', 'union']:
            if policy[1][0] == policy[2][0] and policy[1][0] in ['intersect', 'union']:
                if policy[1][1] == policy[2][2] and policy[1][2] == policy[2][1]:
                    return simplify(policy[1])

        return [operator, simplify(policy[1]), simplify(policy[2])]

    else:
        return policy


def e_step(policy):
    if policy in [0, 1]:
        return policy

    operator = policy[0]
    if operator == 'exec':
        return 0
    elif operator == 'concat':
        return e_step(policy[1]) * e_step(policy[2])
    elif operator == 'intersect':
        return e_step(policy[1]) * e_step(policy[2])
    elif operator == 'union':
        return max(e_step(policy[1]), e_step(policy[2]))
    elif operator == 'star':
        return 1
    elif operator == 'neg':
        return abs(e_step(policy[1]) - 1)
    else:
        raise ValueError(f'Incorrect e_step, input: {policy}.')
