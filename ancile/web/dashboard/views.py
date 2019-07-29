import json
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ancile.web.dashboard.models import *

# Create your views here.

@login_required
def dashboard(request):
    return render(request, "dashboard.html", {})

@login_required
def providers(request):
    tokens = Token.objects.filter(user=request.user)
    return render(request, "user/providers.html", {"tokens" : tokens})

@login_required
def policies(request):
    policies = Policy.objects.filter(user=request.user)
    return render(request, "user/policies.html", {"policies" : policies})

@login_required
def apps(request):
    policies = Policy.objects.filter(user=request.user)
    context = {}
    context["apps"] = [policy.app for policy in policies]
    context["all_apps"] = App.objects.all()
    return render(request, "user/apps.html", context)

@login_required
def get_app_groups(request):
    app = request.POST.get("app")
    if app:
        group_names = [group.name for group in PermissionGroup.objects.filter(app__name=app)]
        return HttpResponse(json.dumps(group_names), content_type="application/json")
    raise Http404

@login_required
def admin_users(request):
    users = User.objects.all()
    return render(request, "admin/users.html", {"users" : users})

@login_required
def admin_tokens(request):
    tokens = Token.objects.all()
    return render(request, "admin/tokens.html", {"tokens" : tokens})

@login_required
def admin_apps(request):
    apps = App.objects.all()
    return render(request, "admin/apps.html", {"apps" : apps})

@login_required
def admin_policies(request):
    policies = Policy.objects.all()
    return render(request, "admin/policies.html", {"policies" : policies})

@login_required
def admin_groups(request):
    groups = PermissionGroup.objects.all()
    return render(request, "admin/groups.html", {"groups" : groups})

@login_required
def admin_providers(request):
    providers = DataProvider.objects.all()
    return render(request, "admin/providers.html", {"providers" : providers})

@login_required
def admin_functions(request):
    functions = Function.objects.all()
    return render(request, "admin/functions.html", {"functions" : functions})

@login_required
def admin_delete_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return redirect("/dashboard/admin/users")

@login_required
def admin_view_user(request, user_id):
    usr = User.objects.get(pk=user_id)
    tokens = Token.objects.filter(user_id=user_id)
    policies = Policy.objects.filter(user_id=user_id)
    return render(request, "admin/view_user.html", {"usr" : usr, "tokens" : tokens, "policies" : policies})

@login_required
def admin_delete_token(request, token_id):
    token = Token.objects.get(pk=token_id)
    user_id = token.user.id
    token.delete()
    return redirect("/dashboard/admin/view/user/" + str(user_id))

@login_required
def admin_view_token(request, token_id):
    token = Token.objects.get(pk=token_id)
    return render(request, "admin/view_token.html", {"token" : token})

@login_required
def admin_delete_policy(request, policy_id):
    policy = Policy.objects.get(pk=policy_id)
    user_id = policy.user.id
    policy.delete()
    return redirect("/dashboard/admin/view/user/" + str(user_id))

@login_required
def admin_view_policy(request, policy_id):
    token = Token.objects.get(pk=token_id)
    return render(request, "admin/view_token.html", {"token" : token})

