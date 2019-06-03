from src.micro_data_core_python.errors import AncileException
from src.micro_data_core_python.policy import Policy
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
        self._policy = Policy(policy)
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
        if self._policy.d_step({'command': command, 'kwargs': kwargs}):
            return True
        else:
            return False

    def _advance_policy_after_comparison(self, command, kwargs=None):
        #print(f'Advancing {command} against policy: {self._policy}')
        self._policy = Policy.d_step(self._policy, {'command': command,
                                                    'kwargs': kwargs})
        if not self._policy:
            raise ValueError('Policy prevented from running')

    def _call_transform(self, func, *args, scope='transform', **kwargs):
        check_is_func(func)
        command = func.__name__
        #print(f'old policy: {self._policy}.')
        self._resolve_private_data_keys(kwargs)
        self._policy = Policy.d_step(self._policy, {'command': command,
                                                    'kwargs': kwargs},
                                     scope=scope)
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
        # print(f'old policy: {self._policy}.')
        self._resolve_private_data_keys(kwargs)
        self._policy = self._policy.d_step({'command': command,
                                            'kwargs': kwargs}, scope=scope)
        # print(f'new policy: {self._policy}, data: {self._data}')
        if self._policy:
            # replace in kwargs:
            self._resolve_private_data_values(kwargs)
            return func(*args, **kwargs)
        else:
            raise ValueError('Policy prevented from running')

    def _call_external(self, func, *args, scope='external', **kwargs):
        check_is_func(func)
        command = func.__name__
        # print(f'old policy: {self._policy}.')
        self._resolve_private_data_keys(kwargs)
        self._policy = self._policy.d_step({'command': command,
                                            'kwargs': kwargs}, scope=scope)
        # print(f'new policy: {self._policy}, data: {self._data}')
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
        self._policy = self._policy.d_step({'command': command,
                                            'kwargs': kwargs}, scope=scope)
        step_result = self._policy.e_step()
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


def check_is_func(func):
    if not callable(func):
        raise AncileException("You can't call operation on the DataPair object. Use only allowed functions.")

