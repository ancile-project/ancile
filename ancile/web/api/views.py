import json
from django.shortcuts import render
# from ancile.core.core import execute
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from ancile.web.dashboard.models import User, Token, PermissionGroup, DataProvider, App

@require_http_methods(["POST"])
def execute_api(request):
    pass

@login_required
@require_http_methods(["POST"])
def check_permission_group(request):
    app_name = request.POST['app']
    group_name = request.POST['group']

    app = App.objects.get(name=app_name)
    perm_group = PermissionGroup.objects.get(name=group_name, app=app)

    provider_scope = {tk.provider:tk.scopes.all() for tk in request.user.tokens}

    return HttpResponse(json.dumps([{"path_name": provider.path_name,
             "display_name": provider.display_name,
             "status": len(set(wanted_scopes) - set(provider_scope.get(provider, set()))) == 0,
             "scopes": [{"simple_name": sc.simple_name,
                         "value": sc.value} for sc in wanted_scopes]
             } for provider, wanted_scopes in perm_group.provider_scope_list]))
