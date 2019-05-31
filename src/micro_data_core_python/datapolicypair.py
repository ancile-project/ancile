from src.micro_data_core_python.errors import AncileException
import datetime


class PrivateData(object):
    """
    Wrapper object that represents data to be substituted in.

    The object stores a keyword. When a PrivateData object is used as a
    parameter to an ancile fn, the key is used to substitute a value from the
    user's private data store.
    """
    def __init__(self, key=None):
        """
        :param str key: The key held by the object. May be none.
        """
        self._key = key

    def __eq__(self, other):
        """Equality check. Used during policy checks."""
        if self is other:
            return True
        elif isinstance(other, self.__class__):
            return self._key == other._key
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f'<PrivateData. {self._key}>'


class DataPolicyPair:
    """An object containing data and the associated policies."""

    def __init__(self, policy, token, name, username, private_data,
                 app_id=None):
        self._name = name
        self._username = username
        self._data = {'output': list()}
        self._policy = policy
        self._token = token
        self._encryption_keys = {}
        self._app_id = app_id
        self._expires_at = None

        if isinstance(private_data, dict) and private_data.get(self._name, False):
            self._private_data = private_data[self._name]
        else:
            self._private_data = {}

    @property
    def is_expired(self):
        """Return a True if the point has expired."""
        if self._expires_at is None:
            return False
        else:
            now = datetime.datetime.utcnow()
            return now > self._expires_at

    def _set_expiry(self, seconds):
        """Update the _expires_at property.

        :param int seconds: The time in seconds until the point expires.
        """
        now = datetime.datetime.utcnow()
        self._expires_at = now + datetime.timedelta(seconds=seconds)

    def __repr__(self):
        return f'<DataPolicy. User: {self._username} Src: {self._name}>'

    def check_command_allowed(self, command, kwargs=None):
        #print(f'Checking {command} against policy: {self._policy}')
        if DataPolicyPair.d_step(self._policy, {'command': command, 'kwargs': kwargs}):
            return True
        else:
            return False

    def _advance_policy_after_comparison(self, command, kwargs=None):
        #print(f'Advancing {command} against policy: {self._policy}')
        self._policy = DataPolicyPair.d_step(self._policy, {'command': command, 
                                                            'kwargs': kwargs})
        if not self._policy:
            raise ValueError('Policy prevented from running') 

    def _call_transform(self, func, *args, scope='transform', **kwargs):
        check_is_func(func)
        command = func.__name__
        #print(f'old policy: {self._policy}.')
        self._resolve_private_data_keys(kwargs)
        self._policy = DataPolicyPair.d_step(self._policy, {'command': command, 'kwargs': kwargs}, scope=scope)
        #print(f'new policy: {self._policy}, data: {self._data}')
        if self._policy:
            # replace in kwargs:
            self._resolve_private_data_values(kwargs)
            kwargs['data'] = self._data
            return func(*args, **kwargs)
        else:
            raise ValueError('Policy prevented from running')

    def _call_store(self, func, *args, scope='store', **kwargs):
        # This is the same as call transform, it just leaves data as the dp_obj
        check_is_func(func)
        command = func.__name__
        #print(f'old policy: {self._policy}.')
        self._resolve_private_data_keys(kwargs)
        self._policy = DataPolicyPair.d_step(self._policy, {'command': command, 'kwargs': kwargs}, scope=scope)
        #print(f'new policy: {self._policy}, data: {self._data}')
        if self._policy:
            # replace in kwargs:
            self._resolve_private_data_values(kwargs)
            return func(*args, **kwargs)
        else:
            raise ValueError('Policy prevented from running')

    def _call_external(self, func, *args, scope='external', **kwargs):
        check_is_func(func)
        command = func.__name__
        #print(f'old policy: {self._policy}.')
        self._resolve_private_data_keys(kwargs)
        self._policy = DataPolicyPair.d_step(self._policy, {'command': command, 'kwargs': kwargs}, scope=scope)
        #print(f'new policy: {self._policy}, data: {self._data}')
        if self._policy:
            self._resolve_private_data_values(kwargs)
            kwargs['data'] = self._data
            kwargs['token'] = self._token
            return func(*args, **kwargs)
        else:
            raise ValueError('Policy prevented from running')

    def _use_method(self, func, *args, scope='return', **kwargs):

        #print(f'return policy: {self._policy}, data: {self._data}')
        check_is_func(func)
        command = func.__name__

        self._resolve_private_data_keys(kwargs)
        self._policy = self.d_step(self._policy, {'command': command, 'kwargs': kwargs}, scope=scope)
        step_result = DataPolicyPair.e_step(self._policy)
        if step_result == 1:
            self._resolve_private_data_values(kwargs)
            kwargs['encryption_keys'] = self._encryption_keys
            kwargs['data'] = self._data
            return func(*args, **kwargs)
        else:
            error = f'Last E step failed: {self._policy}'
            raise ValueError(error)

    def _resolve_private_data_keys(self, kwargs):
        for key, value in kwargs.items():
            if isinstance(value, PrivateData) and value._key is None:
                value._key = key

    def _resolve_private_data_values(self, kwargs):
        for key, value in kwargs.items():
            if isinstance(value, PrivateData):
                kwargs[key] = self._private_data[value._key]

    @staticmethod
    def d_step(policy, command, scope=None):
        """


        :param policy: current policy
        :param command:
        :param scope: a high-level scope of functions (transform, fetch, etc). If scope specified then we check the
        policy against it as well.

        :return:
        """
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
                        #print(f'Checking for key: {key} and value: {value}, passed param: {kwargs.get(key, False)}')
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
            p1 = DataPolicyPair.simplify(['concat', DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command,
                                                                                                  scope
                                                                                                  )), policy[2]])
            p2 = DataPolicyPair.simplify(['concat', DataPolicyPair.e_step(policy[1]), DataPolicyPair.simplify(
                DataPolicyPair.d_step(policy[2], command, scope))])
            return DataPolicyPair.simplify(['union', p1, p2])
        elif operator == 'union':
            p1 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command, scope))
            p2 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[2], command, scope))
            return DataPolicyPair.simplify(['union', p1, p2])
        elif operator == 'star':
            p1 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command, scope))
            p2 = ['star', policy[1]]
            return DataPolicyPair.simplify(['concat', p1, p2])
        elif operator == 'intersect':
            p1 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command, scope))
            p2 = DataPolicyPair.simplify(DataPolicyPair.d_step(policy[2], command, scope))
            return DataPolicyPair.simplify(['intersect', p1, p2])
        elif operator == 'neg':
            return ['neg', DataPolicyPair.simplify(DataPolicyPair.d_step(policy[1], command, scope))]
        else:
            error = f'Cannot process following policy: {policy}.'
            raise ValueError(error)

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
            error = f'Incorrect e_step, input: {policy}.'
            raise ValueError(error)


def check_is_func(func):
    if not callable(func):
        raise AncileException("You can't call operation on the DataPair object. Use only allowed functions.")

