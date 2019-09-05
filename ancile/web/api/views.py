import json
from ancile.core.core import execute
from ancile.web.dashboard.models import App
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ancile.core.user_secrets import UserSecrets
from ancile.web.api.queries import get_app_id, get_user_bundle, get_app_module
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.auth.decorators import login_required
import pika
import dill
from ancile.utils.messaging import RpcClient
from config.loader import configs

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def execute_api(request):
    body = json.loads(request.body)

    logger.info(f"Received request: {body}")
    try:
        token = body["token"]
        users = body["users"]
        program = body["program"]
    except KeyError:
        return JsonResponse({"result": "error",
                             "error": "Missing one or more required paramters: (token, users, program)"})

    try:
        app_id = get_app_id(token)
    except Exception:
        return JsonResponse({"result": "error",
                             "error": "Invalid token"})
    try:
        user_info = [get_user_bundle(user, app_id) for user in users]
    except Exception:
        return JsonResponse({"result": "error",
                             "error": "Problem in retreiving user information"})

    users_secrets = UserSecrets.prepare_users_secrets(user_info, app_id)
    if configs.get('DISTRIBUTED', False):
        user_pickled = dill.dumps((users_secrets, program,
                                   app_id, None))
        rabbit = RpcClient()
        res_dill = rabbit.call(user_pickled)
        res = dill.loads(res_dill)
    else:
        res = execute(users_secrets=users_secrets,
                      program=program,
                      app_id=app_id,
                      app_module=get_app_module(app_id))

    logger.info(f"Returning response: {res}")
    return JsonResponse(res)

@require_http_methods(["POST"])
@login_required
def browser_execute(request):
    user = request.user
    body = json.loads(request.body)

    logger.info(f"Received request: {body}")

    app_id = int(body['app_id'])

    if App.objects.filter(id=app_id, developers=user).exists():
        users = body["users"]
        program = body["program"]
        try:
            user_info = [get_user_bundle(user, app_id) for user in users]
        except Exception:
            return JsonResponse({"result": "error",
                                 "error": "Problem in retreiving user information"})
        res = {'dumb_output': None}
        users_secrets = UserSecrets.prepare_users_secrets(user_info, app_id)
        if configs.get('DISTRIBUTED', False):
            user_pickled = dill.dumps((users_secrets, program,
                                         app_id, None))
            rabbit = RpcClient()
            res_dill = rabbit.call(user_pickled)
            res = dill.loads(res_dill)
        else:
            res = execute(users_secrets=users_secrets,
                            program=program,
                            app_id=app_id,
                            app_module=get_app_module(app_id))
        print(f'Result: {res}')

        return JsonResponse(res)
    else:
        return JsonResponse({"result": "error",
                             "error": "You are not a developer for this app"})
                             "error": "You are not a developer for this app"})


def prepare_user_specific(user_info, app_id):
    users_specific = dict()
    for user in user_info:
        user_specific = UserSecrets(user.policies, user.tokens,
                                    user.private_data,
                                    username=user.username,
                                    app_id=app_id)
        users_specific[user.username] = user_specific
    return users_specific


