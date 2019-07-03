from ancile_web.errors import AncileException, PolicyError
from ancile_core.policy import Policy
from ancile_core.private_data import PrivateData
import ancile_core.time as ancile_web_time
import logging
logger = logging.getLogger(__name__)


class DataPolicyPair:
    """An object containing data and the associated policies."""

    def __init__(self, policy, token, name, username, private_data,
                 app_id=None):
        self._name = name
        self._username = username
        self._data = {'output': list()}
        self._policy = Policy(policy) if not isinstance(policy, Policy) else policy
        self._token = token
        self._encryption_keys = {}
        self._app_id = app_id
        self._expires_at = None
        self._created_at = ancile_web_time.get_timestamp()
        self._was_loaded = False
        self._load_key = ''

        if isinstance(private_data, dict) and private_data.get(self._name, False):
            self._private_data = private_data[self._name]
        else:
            self._private_data = {}

    @property
    def metadata(self):
        return {'name': self._name,
                'username': self._username}


    @property
    def is_expired(self):
        """Return a True if the point has expired."""
        if self._expires_at is None:
            return False
        else:
            return ancile_web_time.get_timestamp() > self._expires_at

    def _set_expiry(self, seconds):
        """Update the _expires_at property.

        :param int seconds: The time in seconds until the point expires.
        """
        self._expires_at = ancile_web_time.get_timestamp_from_now(seconds)

    def __repr__(self):
        return f'<DataPolicy. User: {self._username} Datasource: {self._name}>'

    def check_command_allowed(self, command, kwargs=None):
        if self.is_expired:
            return False
        else:
        #print(f'Checking {command} against policy: {self._policy}')
            return self._policy.check_allowed(command, kwargs)

    def _advance_policy(self, command, update=True, **kwargs):
        logger.info(f'Advancing policy: {self._policy} with command {command}')
        if update:
            self._policy = Policy.d_step(self._policy, {'command': command,
                                                        'kwargs': kwargs})
            return self._policy
        else:
            return Policy.d_step(self._policy, {'command': command,
                                                'kwargs': kwargs})

    def _advance_policy_error(self, command, **kwargs):
        if not self._advance_policy(command, **kwargs):
            raise PolicyError

    def _call(self, func, *args, scope=None, **kwargs):
        if self.is_expired:
            raise ValueError('Cannot use expired expired DataPolicyPair')

        check_is_func(func)
        command = func.__name__
        self._resolve_private_data_keys(kwargs)

        if self._advance_policy(command, **kwargs):
            self._resolve_private_data_values(kwargs)

            if scope in {'transform', 'aggregate'}:
                kwargs['data'] = self._data
            if scope == 'external':
                kwargs['user'] = {'token': self._token}

            if scope == 'return':
                if self._policy.e_step() != 1:
                    raise PolicyError()
                else:
                    kwargs['encryption_keys'] = self._encryption_keys
                    kwargs['data'] = self._data

            return func(*args, **kwargs)
        else:
            raise PolicyError()

    def _call_transform(self, func, *args,  **kwargs):
        return self._call(func, *args, scope='transform', **kwargs)

    def _call_store(self, func, *args, **kwargs):
        return self._call(func, *args, scope='store', **kwargs)

    def _call_external(self, func, *args, **kwargs):
        return self._call(func, *args, scope='external', **kwargs)

    def _use_method(self, func, *args, **kwargs):
        return self._call(func, *args, scope='return', **kwargs)

    def _call_collection(self, func, *args, **kwargs):
        return self._call(func, *args, scope='collection', **kwargs)

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

