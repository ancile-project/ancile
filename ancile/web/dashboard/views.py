import json
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ancile.web.dashboard.models import *
from ancile.web.dashboard.forms import *
from ancile.web.dashboard.decorators import *

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
@user_is_admin
def admin_users(request):
    users = User.objects.all()
    return render(request, "admin/users.html", {"users" : users})

@login_required
@user_is_admin
def admin_tokens(request):
    tokens = Token.objects.all()
    return render(request, "admin/tokens.html", {"tokens" : tokens})

@login_required
@user_is_admin
def admin_apps(request):
    apps = App.objects.all()
    return render(request, "admin/apps.html", {"apps" : apps})

@login_required
@user_is_admin
def admin_policies(request):
    policies = Policy.objects.all()
    return render(request, "admin/policies.html", {"policies" : policies})

@login_required
@user_is_admin
def admin_groups(request):
    groups = PermissionGroup.objects.all()
    return render(request, "admin/groups.html", {"groups" : groups})

@login_required
@user_is_admin
def admin_providers(request):
    providers = DataProvider.objects.all()
    return render(request, "admin/providers.html", {"providers" : providers})

@login_required
@user_is_admin
def admin_functions(request):
    functions = Function.objects.all()
    return render(request, "admin/functions.html", {"functions" : functions})

@login_required
@user_is_admin
def admin_delete_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return redirect("/dashboard/admin/users")

@login_required
@user_is_admin
def admin_view_user(request, user_id):
    usr = User.objects.get(pk=user_id)
    tokens = Token.objects.filter(user_id=user_id)
    policies = Policy.objects.filter(user_id=user_id)
    return render(request, "admin/view_user.html", {"usr" : usr, "tokens" : tokens, "policies" : policies})

@login_required
@user_is_admin
def admin_delete_token(request, token_id):
    token = Token.objects.get(pk=token_id)
    user_id = token.user.id
    token.delete()
    return redirect("/dashboard/admin/view/user/" + str(user_id))

@login_required
@user_is_admin
def admin_view_token(request, token_id):
    token = Token.objects.get(pk=token_id)
    return render(request, "admin/view_token.html", {"token" : token})

@login_required
@user_is_admin
def admin_delete_policy(request, policy_id):
    policy = Policy.objects.get(pk=policy_id)
    user_id = policy.user.id
    policy.delete()
    return redirect("/dashboard/admin/view/user/" + str(user_id))

@login_required
@user_is_admin
def admin_view_policy(request, policy_id):
    policy = Policy.objects.get(pk=policy_id)
    return render(request, "admin/view_policy.html", {"policy" : policy})

@login_required
@user_is_admin
def admin_add_policy(request, user_id):
    if request.method == "POST":
        form = AdminAddPolicyForm(request.POST)

        provider = request.POST.get('provider')
        form.fields['provider'].choices = [(provider, provider)]

        if form.is_valid():
            policy = Policy(text=form.cleaned_data['text'],
                            provider=DataProvider.objects.get(name=form.cleaned_data['provider']),
                            user=User.objects.get(id=user_id),
                            app=App.objects.get(name=form.cleaned_data['app']),
                            active = True if form.cleaned_data['active'] else False)
            policy.save()
            return redirect("/dashboard/admin/view/user/" + str(user_id))
    else:
        user = User.objects.get(id=user_id)
        form = AdminAddPolicyForm(initial={})
        form.fields['provider'].choices=set([(token.provider.name, token.provider.name) for token in Token.objects.filter(user=user)])

    return render(request, 'admin/add_policy.html', {"user_id" : user_id, "form" : form})

@login_required
@user_is_admin
def admin_edit_policy(request, policy_id):
    policy = Policy.objects.get(pk=policy_id)
    user_id = policy.user.id

    if request.method == "POST":
        form = AdminEditPolicyForm(request.POST)

        if form.is_valid():
            policy.text = form.cleaned_data['text']
            policy.active = True if form.cleaned_data['active'] else False
            policy.save()
            return redirect("/dashboard/admin/view/user/" + str(user_id))
    else:
        form = AdminEditPolicyForm(initial={"text" : policy.text, "active" : policy.active})

    return render(request, 'admin/edit_policy.html', {"policy_id" : policy_id, "form" : form})

@login_required
@user_is_admin
def admin_edit_user(request, user_id):
    user = User.objects.get(pk=user_id)

    if request.method == "POST":
        form = AdminEditUserForm(request.POST)

        if form.is_valid():
            user.is_developer = False if form.cleaned_data['apps'] == [] else True
            if user.is_developer:
                for app in user.apps:
                    if app.name not in form.cleaned_data['apps']:
                        app.developers.remove(user)
                for app in form.cleaned_data['apps']:
                    this_app = App.objects.get(name=app)
                    this_app.developers.add(user)
                    this_app.save()

            user.is_superuser = True if form.cleaned_data['is_admin'] else False
            user.save()
            return redirect("/dashboard/admin/view/user/" + str(user_id))
    else:
        form = AdminEditUserForm(initial={"apps" : [app.name for app in user.apps], "is_admin" : user.is_superuser})

    return render(request, 'admin/edit_user.html', {"user_id" : user_id, "form" : form})

@login_required
@user_is_admin
def admin_delete_app(request, app_id):
    app = App.objects.get(pk=app_id)
    app.delete()
    return redirect("/dashboard/admin/apps")

@login_required
@user_is_admin
def admin_view_app(request, app_id):
    app = App.objects.get(pk=app_id)
    developers = app.developers.all()
    groups = PermissionGroup.objects.filter(app=app)
    functions = Function.objects.filter(app=app)
    return render(request, "admin/view_app.html", {"app" : app,
                                                    "developers" : developers,
                                                    "groups" : groups,
                                                    "functions" : functions})

@login_required
@user_is_admin
def admin_edit_app(request, app_id):
    return redirect("/dashboard/admin/apps")

@login_required
@user_is_admin
def admin_delete_group(request, group_id):
    app = App.objects.get(id=group_id.app.id)
    group = PermissionGroup.objects.get(pk=group_id)
    group.delete()
    return redirect("/dashboard/admin/view/app/" + str(app.id))

@login_required
@user_is_admin
def admin_view_group(request, group_id):
    return redirect("/dashboard/admin/apps")

@login_required
@user_is_admin
def admin_add_group(request, group_id):
    return redirect("/dashboard/admin/apps")

@login_required
@user_is_admin
def admin_edit_group(request, group_id):
    return redirect("/dashboard/admin/apps")
