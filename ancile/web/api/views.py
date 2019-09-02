import json
from ancile.core.core import execute
from ancile.web.dashboard.models import App
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ancile.web.api.queries import get_app_id, get_user_bundle, get_app_module
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.auth.decorators import login_required

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

    res = execute(user_info=user_info,
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
        res = execute(user_info=user_info,
                    program=program,
                    app_id=app_id,
                    app_module=get_app_module(app_id))

        logger.info(f"Returning response: {res}")
        return JsonResponse(res)
    else:
        return JsonResponse({"result": "error",
                             "error": "You are not a developer for this app"})