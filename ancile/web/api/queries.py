from config.loader import ENABLE_CACHE, REDIS_CONFIG
from collections import namedtuple
from ancile.web.dashboard import models
import redis
import json
import pickle
import dill
import types
import logging

logger = logging.getLogger(__name__)

UserInfoBundle = namedtuple(
    "UserInfoBundle", ["username", "policies", "tokens", "private_data"]
)

redis = redis.Redis(**REDIS_CONFIG)

MODULE_PREFIX = """
from ancile_core.decorators import transform_decorator
"""


def jsonify(value):
    if isinstance(value, str):
        return json.loads(value)
    else:
        return value


def _get_user_bundle(username, app_id):
    user_id = models.User.objects.filter(username=username).values("id")[0]["id"]
    policies_raw = models.Policy.objects.filter(
        app_id=app_id, user_id=user_id, active=True
    ).values("provider__path_name", "text")

    tokens_raw = models.Token.objects.filter(user_id=user_id)
    tokens = dict()
    for token in tokens_raw:
        if token.expired:
            token.refresh()
        tokens[token.provider.path_name] = token.access_token

    private_data_raw = models.PrivateData.objects.filter(user_id=user_id).values(
        "value", "provider__path_name"
    )

    policies = dict()

    private_data = {
        x["provider__path_name"]: jsonify(x["value"]) for x in private_data_raw
    }

    for policy_dict in policies_raw:
        path_name = policy_dict["provider__path_name"]
        if path_name in policies:
            policies[path_name].append(policy_dict["text"])
        else:
            policies[path_name] = [policy_dict["text"]]

    return UserInfoBundle(
        policies=policies, tokens=tokens, private_data=private_data, username=username
    )


def _get_user_bundle_cache(username, app_id):
    key = f"{username}:{app_id}"
    redis_response = redis.get(key)

    if redis_response:
        bundle = pickle.loads(redis_response)
    else:
        bundle = _get_user_bundle(username, app_id)
        redis.set(key, pickle.dumps(bundle), ex=360)

    return bundle


get_user_bundle = _get_user_bundle_cache if ENABLE_CACHE else _get_user_bundle


def _get_app_id_cache(coded_salt):
    redis_response = redis.get(coded_salt)
    if redis_response:
        app_id = int(redis_response)
    else:
        app_id = models.App.objects.retrieve_app_id(coded_salt)
        redis.set(coded_salt, str(app_id), ex=3600)

    return app_id


def _get_app_id(coded_salt):
    return models.App.objects.retrieve_app_id(coded_salt)


get_app_id = _get_app_id_cache if ENABLE_CACHE else _get_app_id


def _get_app_module(app_id):
    module_text = models.Function.objects.get_app_module(app_id)
    if module_text:
        module_text = MODULE_PREFIX + module_text
        compiled = compile(module_text, "", "exec")

        app = types.ModuleType("app")
        exec(compiled, app.__dict__)
        return app
    else:
        return types.ModuleType("app")


def _get_app_module_cached(app_id):
    key = f"app_module:{app_id}"
    redis_response = redis.get(app_id)

    if redis_response:
        app = dill.loads(redis_response)
    else:
        app = _get_app_module(app_id)
        redis.set(key, dill.dumps(app), ex=600)


get_app_module = _get_app_module_cached if ENABLE_CACHE else _get_app_module
