from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ancile.web.dashboard.models import *

# Create your views here.

@login_required
def dashboard(request):
    is_superuser = request.user.is_superuser
    return render(request, "dashboard.html", {"is_superuser" : is_superuser, "is_developer" : True})

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
    return render(request, "admin/users.html", {})

@login_required
def admin_tokens(request):
    return render(request, "admin/tokens.html", {})

@login_required
def admin_apps(request):
    return render(request, "admin/apps.html", {})

@login_required
def admin_policies(request):
    return render(request, "admin/policies.html", {})

@login_required
def admin_groups(request):
    return render(request, "admin/groups.html", {})

@login_required
def admin_providers(request):
    return render(request, "admin/providers.html", {})

@login_required
def admin_functions(request):
    return render(request, "admin/functions.html", {})
