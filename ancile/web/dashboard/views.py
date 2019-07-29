from django.shortcuts import render
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
    apps = [policy.app for policy in policies]
    return render(request, "user/apps.html", {"apps" : apps})

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
