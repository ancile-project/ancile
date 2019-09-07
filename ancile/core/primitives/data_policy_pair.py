from __future__ import annotations
from copy import copy, deepcopy

from ancile.core.primitives import Policy, Command
from ancile.utils.errors import AncileException, PolicyError
from ancile.core.primitives.policy_helpers.private_data import PrivateData
import ancile.utils.time as ancile_web_time
import logging
import uuid
logger = logging.getLogger(__name__)


class DataPolicyPair:
    """An object containing data and the associated policies."""
    _policy: Policy

    def __init__(self, policy=None, token=None, name=None, username=None, private_data=None,
                 app_id=None):
        """

        :param policy: instance of the policy
        :param token: access token to retrieve data
        :param name: custom name that can help identify the DPP, usually a DataSource name
        :param username:
        :param private_data:
        :param app_id:
        """
        self._uuid = uuid.uuid1().hex
        self._name = name
        self._username = username
        self._data = dict()
        self._policy = Policy(policy) if policy else None
        self._token = token
        self._encryption_keys = {}
        self._app_id = app_id
        self._expires_at = None
        self._created_at = ancile_web_time.get_timestamp()
        self._was_loaded = False
        self._load_key = ''

        self._previous_dpp = {}

        if isinstance(private_data, dict) and private_data.get(self._name, False):
            self._private_data = private_data[self._name]
        else:
            self._private_data = {}

    @property
    def metadata(self):
        return {'name': self._name, 'uuid': self._uuid,
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
        dpp._previous_dpp = {self._uuid, self}
        dpp._was_loaded = self._was_loaded
        dpp._load_key = self._load_key

        return dpp

    def __getitem__(self, item):
        dpp = copy(self)
        dpp._data = dpp._data[item]

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
        return f'<DataPolicy. User: {self._username} Datasource: {self._name}. Policy: {self._policy}>'


    @classmethod
    def combine_dpps_list(cls, dpp_list):
        """
        Combine dpps when they are provided as a list. Not used yet.
        """

        new_dpp = deepcopy(dpp_list[0])
        new_dpp._data = [new_dpp._data]
        for dpp in dpp_list[1:]:
            if new_dpp._name != dpp._name:
                new_dpp._name = f'{new_dpp._name}, {dpp._name}'
            if new_dpp._username != dpp._username:
                new_dpp._username = f'{new_dpp._username}, {dpp._username}'
            if new_dpp._token != dpp._token:
                new_dpp._token = {new_dpp._uuid: new_dpp._token, dpp._uuid: dpp._token}
            new_dpp._policy = new_dpp._policy.intersect(dpp._policy)
            new_dpp._previous_dpp[dpp._uuid] = dpp
            new_dpp._data.append(dpp._data)

        return new_dpp

    @classmethod
    def combine_dpps_dict(cls, dpp_dict):
        """
        Combine DPPs when they are provided as a dict.

        :param dpp_dict:
        :return:
        """

        new_dpp = None
        for key, dpp in dpp_dict.items():
            if new_dpp is None:
                new_dpp = deepcopy(dpp)
                new_dpp._data = {}
            else:
                if new_dpp._name != dpp._name:
                    new_dpp._name = f'{new_dpp._name}, {dpp._name}'
                if new_dpp._username != dpp._username:
                    new_dpp._username = f'{new_dpp._username}, {dpp._username}'
                if new_dpp._token != dpp._token:
                    new_dpp._token = {new_dpp._uuid: new_dpp._token, dpp._uuid: dpp._token}
                new_dpp._policy = new_dpp._policy.intersect(dpp._policy)

            new_dpp._data[key] = dpp._data
            new_dpp._previous_dpp[dpp._uuid] = dpp

        return new_dpp


    def check_command_allowed(self, command, **kwargs):
        if self.is_expired:
            return False
        else:
            return bool(self._policy)

    def _advance_policy(self, command, update=True):

        return self._policy.advance_policy(command, update)

    def _advance_policy_error(self, command):
        previous_policy = copy(self._policy)
        self._advance_policy(command, update=True)
        if not self._policy:
            raise PolicyError(message=f'Cannot advance policy: {previous_policy} with policy_command: {command}')

    def check_call(self, command):
        if self.is_expired:
            raise ValueError('Cannot use expired expired DataPolicyPair')
        if not isinstance(command, Command):
            raise ValueError(f'This call accepts Command object, check with docs, got: {command}')
        self._resolve_private_data_keys(command.params)
        self._advance_policy_error(command)
        self._resolve_private_data_values(command.params)

    def _call_transform(self, command: Command, keys='data'):
        """
        If the policy check succeeds pass data argument
        as parameter and call the function
        """
        self.check_call(command)
        if isinstance(keys, list):
            for key in keys:
                command.params[key] = self._data[key]
        else:
            command.params[keys] = self._data
        return command.call()

    def _call_store(self, command):
        self.check_call(command)
        return command.call()

    def _call_external(self, command):
        self.check_call(command)
        command.params['user'] = {'token': self._token}
        return command.call()

    def _use_method(self, command):
        """
        advance the policy first with return command and then check if it has
        finished.

        """
        self._advance_policy_error(command)
        if not self._policy.check_finished():
            raise PolicyError(f'The policy has not finished: {self._policy}. E-step failed.')
        command.params['encryption_keys'] = self._encryption_keys
        command.params['data'] = self._data

        return command.call()

    def _call_collection(self, func, *args, **kwargs):
        raise NotImplemented

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

