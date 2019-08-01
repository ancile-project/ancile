import json
from django.shortcuts import render
# from ancile.core.core import execute
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from ancile.web.api.queries import get_app_id, get_user_bundle, get_app_module
from ancile.web.dashboard.models import User, Token, PermissionGroup, DataProvider, App, PolicyTemplate, Policy, Scope
import traceback

@require_http_methods(["POST"])
def execute_api(request):
    try:
        token = request.POST["token"]
        users = request.POST["users"]
        program = request.POST["program"]
    except KeyError:
        return JsonResponse({"status": "error",
                             "error": "Missing one or more required paramters: (token, users, program)"})

    try:
        app_id = get_app_id(token)
    except Exception:
        return JsonResponse({"status": "error",
                             "error": "Invalid token"})
    try:
        user_info = [get_user_bundle(user, app_id) for user in users]
    except Exception:
        return JsonResponse({"status": "error",
                             "error": "Problem in retreiving user information"})

    # res = execute(user_info=user_info,
    #               program=program,
    #               app_id=app_id,
    #               app_module=get_app_module(app_id))
    
    # return JsonResponse(res)



@login_required
@require_http_methods(["POST"])
def check_permission_group(request):
    app_name = request.POST['app']
    group_name = request.POST['group']

    app = App.objects.get(name=app_name)
    perm_group = PermissionGroup.objects.get(name=group_name, app=app)

    provider_scope = {tk.provider:tk.scopes.all() for tk in request.user.tokens}

    return JsonResponse({"description": perm_group.description, "providers": [{"path_name": provider.path_name,
             "display_name": provider.display_name,
             "status": len(set(wanted_scopes) - set(provider_scope.get(provider, set()))) == 0 and provider in provider_scope, 
             "scopes": [{"simple_name": sc.simple_name,
                         "value": sc.value} for sc in wanted_scopes]
             } for provider, wanted_scopes in perm_group.provider_scope_list]})

@login_required
@require_http_methods(["POST"])
def add_predefined_policy_to_user(request):
    try:
        app_name = request.POST['app']
        group_name = request.POST['group']

        app = App.objects.get(name=app_name)
        perm_group = PermissionGroup.objects.get(name=group_name, app=app)

        needed_policies = PolicyTemplate.objects.filter(group=perm_group,
                                                          app=app)
        
        new_policies = []

        for policy in needed_policies:
            if not Token.objects.filter(provider=policy.provider):
                raise Exception("Provider not found")

            new_policy = Policy(
                text=policy.text,
                provider=policy.provider,
                user=request.user,
                app=app,
                active=True
            )

            new_policies.append(new_policy)
        
        for policy in new_policies:
            policy.save()

        return JsonResponse({"status": "ok"})
    except Exception:
        return JsonResponse({"status": "error", "error": "An error has occurred."})

@login_required
@require_http_methods(["POST"])
def remove_app_for_user(request):
    try:
        app_name = request.POST['app']
        app = App.objects.get(name=app_name)
        user_policies = Policy.objects.filter(user=request.user,
                                              app=app)
        user_policies.delete()
        
        return JsonResponse({"status": "ok"})
    except Exception:
        return JsonResponse({"status": "error", "error": "An error has occurred."})

@login_required
@require_http_methods(["POST"])
def get_app_groups(request):
    app = request.POST.get("app")
    if app:
        group_names = [group.name for group in PermissionGroup.objects.filter(app__name=app)]
        return JsonResponse(group_names, safe=False)
    raise Http404

@login_required
@require_http_methods(["POST"])
def remove_provider_for_user(request):
    try:
        provider_path = request.POST["provider"]
        provider = DataProvider.objects.get(path_name=provider_path)
        token = Token.objects.get(provider=provider,
                                  user=request.user)
        token.delete()
        return JsonResponse({"status": "ok"})
    except Exception:
        return JsonResponse({"status": "error", "error": "An error has occurred."})

@login_required
@require_http_methods(["POST"])
def get_provider_scopes(request):
    try:
        provider_path = request.POST["provider"]
        provider = DataProvider.objects.get(path_name=provider_path)
        scopes = Scope.objects.filter(provider=provider)

        scopes_json = [
            {
                "simple_name": scope.simple_name,
                "value": scope.value,
                "description": scope.description
            } for scope in scopes
        ]

        return JsonResponse(scopes_json, safe=False)
    except Exception:
        print(traceback.format_exc())
        return JsonResponse({"status": "error", "error": "An error has occurred."})