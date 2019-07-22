from ancile.utils.errors import AncileException, PolicyError
from core.policy import Policy
from core.private_data import PrivateData
import core.time as ancile_web_time
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

        # FWIW, keep a link to the last DPP
        self._previous_dpp = None

        if isinstance(private_data, dict) and private_data.get(self._name, False):
            self._private_data = private_data[self._name]
        else:
            self._private_data = {}

    @property
    def metadata(self):
        return {'name': self._name,
                'username': self._username}

    def __copy__(self):
        """
        Create a new copy of the object with new field _created_app and set
        the _previous_dpp to recover the previous objects
        :return:
        """
        dpp = DataPolicyPair(policy=self._policy, token=self._token,
                             name=self._name, username=self._username,
                             private_data=self._private_data, app_id=self._app_id)
        if self._data is not None:
            dpp._data = self._data.copy()
        else:
            dpp._data = None
        dpp._expires_at = self._expires_at
        dpp._previous_dpp = self
        dpp._was_loaded = self._was_loaded
        dpp._load_key = self._load_key

        return dpp

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

    def check_command_allowed(self, command, **kwargs):
        if self.is_expired:
            return False
        else:
        #print(f'Checking {command} against policy: {self._policy}')
            return self._policy.check_allowed(command, **kwargs)

    def _advance_policy(self, command, scope=None, update=True, **kwargs):
        if update:
            self._policy = self._policy.d_step({'command': command,
                                                'kwargs': kwargs},
                                                scope=scope)
            return self._policy
        else:
            return self._policy.d_step({'command': command, 'kwargs': kwargs},
                                        scope=scope)

    def _advance_policy_error(self, command, **kwargs):
        new_policy = self._advance_policy(command, **kwargs)
        if not new_policy:
            raise PolicyError
        else: return new_policy

    def _call(self, func, *args, scope=None, **kwargs):
        if self.is_expired:
            raise ValueError('Cannot use expired expired DataPolicyPair')

        check_is_func(func)
        command = func.__name__
        self._resolve_private_data_keys(kwargs)

        if self._advance_policy_error(command, scope=scope, **kwargs):
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

