import json
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ancile.web.dashboard.models import *
from ancile.web.dashboard.forms import *
from ancile.web.dashboard.decorators import *
from django.urls import reverse_lazy
from django.views import generic
from django.template import RequestContext

# Create your views here.
class SignUp(generic.CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'


def dashboard(request):
    return render(request, "dashboard.html", {})

@login_required
def providers(request):
    tokens = Token.objects.filter(user=request.user)
    return render(request, "user/providers.html", {"tokens" : tokens, "all_providers": DataProvider.objects.all})

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
    return redirect("/admin/users")

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
    return redirect("/admin/view/user/" + str(user_id))

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
    return redirect("/admin/view/user/" + str(user_id))

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
                            provider=DataProvider.objects.get(path_name=form.cleaned_data['provider']),
                            user=User.objects.get(id=user_id),
                            app=App.objects.get(name=form.cleaned_data['app']),
                            active = True if form.cleaned_data['active'] else False)
            policy.save()
            return redirect("/admin/view/user/" + str(user_id))
    else:
        user = User.objects.get(id=user_id)
        form = AdminAddPolicyForm(initial={})
        form.fields['provider'].choices=set([(token.provider.path_name, token.provider.display_name) for token in Token.objects.filter(user=user)])

    return render(request, 'admin/form.html', {"redirect" : "/admin/add/policy/" + str(user_id),
                                                "back" : "/admin/view/user/" + str(user_id),
                                                "title" : "Add Policy",
                                                "form_title" : "Add Policy",
                                                "form" : form})

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
            return redirect("/admin/view/user/" + str(user_id))
    else:
        form = AdminEditPolicyForm(initial={"text" : policy.text, "active" : policy.active})

    return render(request, 'admin/form.html', {"redirect" : "/admin/edit/policy/" + str(policy_id),
                                                "back" : "/admin/view/user/" + str(user_id),
                                                "title" : "Edit Policy",
                                                "form_title" : "Edit Policy",
                                                "form" : form})

@login_required
@user_is_admin
def admin_edit_user(request, user_id):
    user = User.objects.get(pk=user_id)

    if request.method == "POST":
        form = AdminEditUserForm(request.POST)

        if form.is_valid():
            user.is_developer = True if form.cleaned_data['is_developer'] else False
            if user.is_developer:
                for app in user.apps:
                    if app.name not in form.cleaned_data['apps']:
                        app.developers.remove(user)
                        app.save()
                for app in form.cleaned_data['apps']:
                    this_app = App.objects.get(name=app)
                    this_app.developers.add(user)
                    this_app.save()

            user.is_superuser = True if form.cleaned_data['is_admin'] else False
            user.save()
            return redirect("/admin/view/user/" + str(user_id))
    else:
        form = AdminEditUserForm(initial={"apps" : [app.name for app in user.apps],
                                            "is_admin" : user.is_superuser,
                                            "is_developer" : user.is_developer})

    return render(request, 'admin/form.html', {"redirect" : "/admin/edit/user/" + str(user_id),
                                                "back" : "/admin/view/user/" + str(user_id),
                                                "title" : "Edit User",
                                                "form_title" : "Edit User",
                                                "user_id" : user_id, "form" : form})

@login_required
@user_is_admin
def admin_delete_app(request, app_id):
    app = App.objects.get(pk=app_id)
    app.delete()
    return redirect("/admin/apps")

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
    app = App.objects.get(pk=app_id)

    if request.method == "POST":
        form = AdminEditAppForm(request.POST)

        if form.is_valid():
            app.name = form.cleaned_data["name"]
            app.description = form.cleaned_data["description"]
            app.developers.clear()
            for dev in form.cleaned_data["developers"]:
                dev_user = User.objects.get(username=dev)
                app.developers.add(dev_user)
            app.save()
            return redirect("/admin/view/app/" + str(app_id))
    else:
        form = AdminEditAppForm(initial={"developers" : [usr.username for usr in app.developers.all()],
                                            "name" : app.name,
                                            "description" : app.description,
                                            "app_id" : app_id})

    return render(request, 'admin/form.html', {"redirect" : "/admin/edit/app/" + str(app_id),
                                                "back" : "/admin/view/app/" + str(app_id),
                                                "title" : "Edit App",
                                                "form_title" : "Edit App",
                                                "app_id" : app_id,
                                                "form" : form})

@login_required
@user_is_admin
def admin_delete_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    app = group.app
    group.delete()
    return redirect("/admin/view/app/" + str(app.id))

@login_required
@user_is_admin
def admin_view_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    policies = PolicyTemplate.objects.filter(group_id=group.id)
    scopes = group.scopes.all()
    return render(request, "admin/view_group.html", {"group" : group,
                                                        "policies" : policies,
                                                        "app" : group.app,
                                                        "scopes" : scopes})

@login_required
@user_is_admin
def admin_add_group(request, app_id):
    if request.method == "POST":
        form = AdminAddGroupForm(request.POST)

        if form.is_valid():
            group = PermissionGroup(name = form.cleaned_data['name'],
                            description = form.cleaned_data['description'],
                            approved = True if form.cleaned_data['approved'] else False,
                            app_id=app_id)

            group.save()
            group.scopes.set([Scope.objects.get(value=scp) for scp in form.cleaned_data['scopes']])
            group.save()
            return redirect("/admin/view/app/" + str(app_id))
    else:
        form = AdminEditGroupForm()

    return render(request, 'admin/form.html', {"redirect" : "/admin/add/group/" + str(app_id),
                                                "back" : "/admin/view/app/" + str(app_id),
                                                "title" : "Add Group",
                                                "form_title" : "Add Group",
                                                "form" : form})

@login_required
@user_is_admin
def admin_edit_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    app_id = group.app.id

    if request.method == "POST":
        form = AdminEditGroupForm(request.POST)
        print(group)

        if form.is_valid():
            group.name = form.cleaned_data['name']
            group.description = form.cleaned_data['description']
            group.scopes.clear()
            group.scopes.set([Scope.objects.get(value=scp) for scp in form.cleaned_data['scopes']])
            group.approved = True if form.cleaned_data['approved'] else False
            print(group.approved)
            group.save()
            return redirect("/admin/view/app/" + str(app_id))
    else:
        form = AdminEditGroupForm(initial={"name" : group.name,
                                            "description" : group.description,
                                            "approved" : group.approved,
                                            "scopes" : [scp.value for scp in group.scopes.all()]})

    return render(request, 'admin/form.html', {"redirect" : "/admin/edit/group/" + str(group_id),
                                                "back" : "/admin/view/group/" + str(group_id),
                                                "title" : "Edit Group",
                                                "form_ title" : "Edit Group",
                                                 "form" : form})

@login_required
@user_is_admin
def admin_delete_function(request, function_id):
    function = Function.objects.get(pk=function_id)
    app = App.objects.get(id=function.app.id)
    function.delete()
    return redirect("/admin/view/app/" + str(app.id))

@login_required
@user_is_admin
def admin_view_function(request, function_id):
    function = Function.objects.get(pk=function_id)
    return render(request, "admin/view_function.html", {"function" : function})

@login_required
@user_is_admin
def admin_add_function(request, app_id):
    print(app_id)
    if request.method == "POST":
        form = AdminAddFunctionForm(request.POST)

        if form.is_valid():
            function = Function(name = form.cleaned_data['name'],
                            description = form.cleaned_data['description'],
                            body = form.cleaned_data['body'],
                            approved = True if form.cleaned_data["approved"] else False,
                            app_id=app_id)

            function.save()
            return redirect("/admin/view/app/" + str(app_id))
    else:
        form = AdminAddFunctionForm()

    return render(request, 'admin/form.html', {"redirect" : "/admin/add/function/" + str(app_id),
                                                "back" : "/admin/view/app/" + str(app_id),
                                                "title" : "Add Function",
                                                "form_title" : "Add Function",
                                                "form" : form})

@login_required
@user_is_admin
def admin_edit_function(request, function_id):
    function = Function.objects.get(pk=function_id)

    if request.method == "POST":
        form = AdminEditFunctionForm(request.POST)

        if form.is_valid():
            function.name = form.cleaned_data["name"]
            function.description = form.cleaned_data["description"]
            function.body = form.cleaned_data["body"]
            function.app_id = form.cleaned_data["app_id"]
            function.approved = True if form.cleaned_data["approved"] else False
            function.save()
            return redirect("/admin/view/app/" + str(function.app_id))
    else:
        form = AdminEditFunctionForm(initial={"name" : function.name,
                                                "description" : function.description,
                                                "approved" : function.approved,
                                                "app_id" : function.app.id,
                                                "body" : function.body})

    return render(request, 'admin/form.html', {"redirect" : "/admin/edit/function/" + str(function_id),
                                                "back" : "/admin/view/app/" + str(function.app.id),
                                                "title" : "Edit Function",
                                                "form_title" : "Edit Function",
                                                "form" : form})

@login_required
@user_is_admin
def admin_delete_policy_template(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    group_id = policy.group.id
    policy.delete()
    return redirect("/admin/view/group/" + str(group_id))

@login_required
@user_is_admin
def admin_view_policy_template(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    return render(request, "admin/view_policy_template.html", {"policy" : policy})

@login_required
@user_is_admin
def admin_add_policy_template(request, group_id):
    if request.method == "POST":
        form = AdminAddPolicyTemplateForm(request.POST)

        if form.is_valid():
            group = PermissionGroup.objects.get(id=group_id)
            policy = PolicyTemplate(text=form.cleaned_data['text'],
                            provider=DataProvider.objects.get(path_name=form.cleaned_data['provider']),
                            group=group,
                            app=group.app)
            policy.save()
            return redirect("/admin/view/group/" + str(group_id))
    else:
        form = AdminAddPolicyTemplateForm()

    return render(request, 'admin/form.html', {"redirect" : "/admin/add/policy/template/" + str(group_id),
                                                "back" : "/admin/view/group/" + str(group_id),
                                                "title" : "Add Policy",
                                                "form_title" : "Add Policy",
                                                "form" : form})

@login_required
@user_is_admin
def admin_edit_policy_template(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    group_id = policy.group.id

    if request.method == "POST":
        form = AdminEditPolicyTemplateForm(request.POST)

        if form.is_valid():
            policy.text = form.cleaned_data['text']
            policy.provider = DataProvider.objects.get(path_name=form.cleaned_data['provider'])
            policy.save()
            return redirect("/admin/view/group/" + str(group_id))
    else:
        form = AdminEditPolicyTemplateForm(initial={"text" : policy.text, "provider" : policy.provider.path_name})

    return render(request, 'admin/form.html', {"redirect" : "/admin/edit/policy/template/" + str(policy_id),
                                                "back" : "/admin/view/group/" + str(group_id),
                                                "title" : "Edit Policy",
                                                "form_title" : "Edit Policy",
                                                "form" : form})

@login_required
@user_is_admin
def admin_delete_provider(request, provider_id):
    provider = DataProvider.objects.get(pk=provider_id)
    provider.delete()
    return redirect("/admin/provider")

@login_required
@user_is_admin
def admin_view_provider(request, provider_id):
    provider = DataProvider.objects.get(pk=provider_id)
    scopes = Scope.objects.filter(provider_id=provider_id)
    params = json.loads(provider.extra_params)
    return render(request, "admin/view_provider.html", {"provider" : provider,
                                                        "scopes" : scopes,
                                                        "extra_params" : params})

@login_required
@user_is_admin
def admin_add_provider(request):
    if request.method == "POST":
        form = AdminAddProviderForm(request.POST)

        if form.is_valid():
            provider = DataProvider(path_name=form.cleaned_data['path_name'],
                                    display_name=form.cleaned_data['display_name'],
                                    access_token_url=form.cleaned_data['token_url'],
                                    auth_url=form.cleaned_data['auth_url'],
                                    client_id=form.cleaned_data['client_id'],
                                    client_secret=form.cleaned_data['client_secret'],
                                    extra_params=form.cleaned_data['json'])
            provider.save()
            return redirect("/admin/providers")
    else:
        form = AdminAddProviderForm(initial={})

    return render(request, 'admin/form.html', {"redirect" : "/admin/add/provider",
                                                "back" : "/admin/providers",
                                                "title" : "Add Provider",
                                                "form_title" : "Add Provider",
                                                "form" : form})

@login_required
@user_is_admin
def admin_edit_provider(request, provider_id):
    provider = DataProvider.objects.get(pk=provider_id)

    if request.method == "POST":
        form = AdminAddProviderForm(request.POST)

        if form.is_valid():
            provider.path_name = form.cleaned_data['path_name']
            provider.display_name = form.cleaned_data['display_name']
            provider.access_token_url = form.cleaned_data['token_url']
            provider.auth_url = form.cleaned_data['auth_url']
            provider.client_id = form.cleaned_data['client_id']
            provider.client_secret = form.cleaned_data['client_secret']
            provider.extra_params = form.cleaned_data['json']
            provider.save()
            return redirect("/admin/view/provider/" + str(provider_id))
    else:
        form = AdminAddProviderForm(initial={"path_name" : provider.path_name,
                                                "display_name" : provider.display_name,
                                                "token_url" : provider.access_token_url,
                                                "auth_url" : provider.auth_url,
                                                "client_id" : provider.client_id,
                                                "client_secret" : provider.client_secret,
                                                "json" : provider.extra_params})

    return render(request, 'admin/form.html', {"redirect" : "/admin/edit/provider/" + str(provider_id),
                                                "back" : "/admin/view/provider/" + str(provider_id),
                                                "title" : "Edit Provider",
                                                "form_title" : "Edit Provider",
                                                "form" : form})

@login_required
@user_is_admin
def admin_delete_scope(request, scope_id):
    scope = Scope.objects.get(pk=scope_id)
    provider_id = scope.provider.id
    scope.delete()
    return redirect("/admin/view/provider/" + str(provider_id))

@login_required
@user_is_admin
def admin_add_scope(request, provider_id):
    if request.method == "POST":
        form = AdminAddScopeForm(request.POST)

        if form.is_valid():
            scope = Scope(simple_name=form.cleaned_data['simple_name'],
                            value=form.cleaned_data['value'],
                            description=form.cleaned_data['description'],
                            provider=DataProvider.objects.get(pk=provider_id))
            scope.save()
            return redirect("/admin/view/provider/" + str(provider_id))
    else:
        form = AdminAddScopeForm(initial={})

    return render(request, 'admin/form.html', {"redirect" : "/admin/add/scope/" + str(provider_id),
                                                "back" : "/admin/view/provider/" + str(provider_id),
                                                "title" : "Add Scope",
                                                "form_title" : "Add Scope",
                                                "form" : form})

@login_required
@user_is_admin
def admin_edit_scope(request, scope_id):
    scope = Scope.objects.get(pk=scope_id)

    if request.method == "POST":
        form = AdminEditScopeForm(request.POST)

        if form.is_valid():
            scope.simple_name = form.cleaned_data['simple_name']
            scope.value = form.cleaned_data['value']
            scope.description = form.cleaned_data['description']
            scope.provider = DataProvider.objects.get(path_name=form.cleaned_data['provider'])
            scope.save()
            return redirect("/admin/view/provider/" + str(scope.provider.id))
    else:
        form = AdminEditScopeForm(initial={"simple_name" : scope.simple_name,
                                                "value" : scope.value,
                                                "description" : scope.description,
                                                "provider" : scope.provider.path_name})

    return render(request, 'admin/form.html', {"redirect" : "/admin/edit/scope/" + str(scope_id),
                                                "back" : "/admin/view/provider/" + str(scope.provider.id),
                                                "title" : "Edit Scope",
                                                "form_title" : "Edit Scope",
                                                "form" : form})


@login_required
@user_is_developer
def dev_console(request):
    return render(request, "dev/console.html", {"apps" : request.user.apps})

@login_required
@user_is_developer
def dev_delete_app(request, app_id):
    app = App.objects.get(pk=app_id)
    if app in request.user.apps:
        app.delete()
    return render(request, "dev/console.html", {"apps" : request.user.apps})

@login_required
@user_is_developer
def dev_view_app(request, app_id):
    app = App.objects.get(pk=app_id)
    if app in request.user.apps:
        groups = PermissionGroup.objects.filter(app=app)
        functions = Function.objects.filter(app=app)
        return render(request, "dev/view_app.html", {"app" : app,
                                                        "groups" : groups,
                                                        "functions" : functions})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_add_app(request):
    if request.method == "POST":
        form = DevEditAppForm(request.POST)

        if form.is_valid():
            app = App(name=form.cleaned_data['name'],
                        description=form.cleaned_data['description'])
            app.save()
            app.developers.set([User.objects.get(username=dev) for dev in form.cleaned_data['developers']])
            app.save()
            return redirect("/dev")
    else:
        form = DevEditAppForm(initial={"developers" : [request.user.username]})

    return render(request, 'dev/form.html', {"redirect" : "/dashboard/dev/add/app",
                                                "back" : "/dashboard/dev",
                                                "title" : "Create App",
                                                "form_title" : "Create App",
                                                "form" : form})

@login_required
@user_is_developer
def dev_edit_app(request, app_id):
    app = App.objects.get(pk=app_id)
    if app in request.user.apps:
        if request.method == "POST":
            form = DevEditAppForm(request.POST)

            if form.is_valid():
                app.name=form.cleaned_data['name']
                app.description=form.cleaned_data['description']
                app.save()
                app.developers.set([User.objects.get(username=dev) for dev in form.cleaned_data['developers']])
                app.save()
                return redirect("/dev")
        else:
            form = DevEditAppForm(initial={"name" : app.name,
                                            "description" : app.description,
                                            "developers" : [dev.username for dev in app.developers.all()]})

        return render(request, 'dev/form.html', {"redirect" : "/dev/edit/app/" + str(app_id),
                                                    "back" : "/dev",
                                                    "title" : "Edit App",
                                                    "form_title" : "Edit App",
                                                    "form" : form})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_delete_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    app_id = group.app.id
    if group.app in request.user.apps:
        group.delete()
    return redirect("/dev/view/app/" + str(app_id))

@login_required
@user_is_developer
def dev_view_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    if group.app in request.user.apps:
        policies = PolicyTemplate.objects.filter(group=group)
        return render(request, "dev/view_group.html", {"group" : group,
                                                        "policies" : policies,
                                                        "scopes" : group.scopes.all()})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_add_group(request, app_id):
    app = App.objects.get(pk=app_id)
    if app in request.user.apps:
        if request.method == "POST":
            form = DevEditGroupForm(request.POST)

            if form.is_valid():
                group = PermissionGroup(app_id=app_id,
                                        name=form.cleaned_data['name'],
                                        description=form.cleaned_data['description'])
                group.save()
                group.scopes.set([Scope.objects.get(value=scp) for scp in form.cleaned_data['scopes']])
                group.save()
                return redirect("/dev/view/app/" + str(app_id))
        else:
            form = DevEditGroupForm()

        return render(request, 'dev/form.html', {"redirect" : "/dev/add/group/" + str(app_id),
                                                    "back" : "/dev/view/app" + str(app_id),
                                                    "title" : "Add Group",
                                                    "form_title" : "Add Group",
                                                    "form" : form})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_edit_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    app = App.objects.get(pk=group.app.id)
    if app in request.user.apps:
        if request.method == "POST":
            form = DevEditGroupForm(request.POST)

            if form.is_valid():
                group.name=form.cleaned_data['name']
                group.description=form.cleaned_data['description']
                group.approved = False
                group.save()
                group.scopes.set([Scope.objects.get(value=scp) for scp in form.cleaned_data['scopes']])
                group.save()
                return redirect("/dev/view/app/" + str(app.id))
        else:
            form = DevEditGroupForm(initial={"name" : group.name,
                                            "description" : group.description,
                                            "scopes" : [scope.value for scope in group.scopes.all()]})

        return render(request, 'dev/form.html', {"redirect" : "/dev/edit/group/" + str(group_id),
                                                    "back" : "/dev/view/app/" + str(app.id),
                                                    "title" : "Edit Group",
                                                    "form_title" : "Edit Group",
                                                    "form" : form})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_delete_policy(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    group_id = policy.group.id
    if policy.app in request.user.apps:
        policy.delete()
    return redirect("/dev/view/group" + str(group_id))

@login_required
@user_is_developer
def dev_view_policy(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    if policy.app in request.user.apps:
        return render(request, "dev/view_policy.html", {"policy" : policy})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_add_policy(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    if group.app in request.user.apps:
        if request.method == "POST":
            form = DevEditPolicyTemplateForm(request.POST)

            if form.is_valid():
                policy = PolicyTemplate(app=group.app,
                                        group=group,
                                        text=form.cleaned_data['text'],
                                        provider=DataProvider.objects.get(path_name=form.cleaned_data['provider']))
                policy.save()
                group.approved = False
                group.save()
                return redirect("/dev/view/group/" + str(group_id))
        else:
            form = DevEditPolicyTemplateForm()

        return render(request, 'dev/form.html', {"redirect" : "/dev/add/policy/template/" + str(group_id),
                                                    "back" : "/dev/view/group/" + str(group_id),
                                                    "title" : "Add Policy",
                                                    "form_title" : "Add Policy",
                                                    "form" : form})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_edit_policy(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    if policy.app in request.user.apps:
        if request.method == "POST":
            form = DevEditPolicyTemplateForm(request.POST)

            if form.is_valid():
                policy.text = form.cleaned_data['text']
                policy.provider = DataProvider.objects.get(path_name=form.cleaned_data['provider'])
                policy.save()
                policy.group.approved = False
                policy.group.save()
                return redirect("/dev/view/group/" + str(policy.group.id))
        else:
            form = DevEditPolicyTemplateForm(initial={"text" : policy.text,
                                                        "provider" : policy.provider.path_name})

        return render(request, 'dev/form.html', {"redirect" : "/dev/edit/policy/template/" + str(policy_id),
                                                    "back" : "/dev/view/group/" + str(policy.group.id),
                                                    "title" : "Edit Policy",
                                                    "form_title" : "Edit Policy",
                                                    "form" : form})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_delete_policy(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    group_id = policy.group.id
    if policy.app in request.user.apps:
        policy.delete()
    return redirect("/dev/view/group" + str(group_id))

@login_required
@user_is_developer
def dev_view_policy(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    if policy.app in request.user.apps:
        return render(request, "dev/view_policy.html", {"policy" : policy})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_add_policy(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    if group.app in request.user.apps:
        if request.method == "POST":
            form = DevEditPolicyTemplateForm(request.POST)

            if form.is_valid():
                policy = PolicyTemplate(app=group.app,
                                        group=group,
                                        text=form.cleaned_data['text'],
                                        provider=DataProvider.objects.get(path_name=form.cleaned_data['provider']))
                policy.save()
                group.approved = False
                group.save()
                return redirect("/dev/view/group/" + str(group_id))
        else:
            form = DevEditPolicyTemplateForm()

        return render(request, 'dev/form.html', {"redirect" : "/dev/add/policy/template/" + str(group_id),
                                                    "back" : "/dev/view/group/" + str(group_id),
                                                    "title" : "Add Policy",
                                                    "form_title" : "Add Policy",
                                                    "form" : form})
    else:
        return redirect("/dev")

@login_required
@user_is_developer
def dev_edit_policy(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    if policy.app in request.user.apps:
        if request.method == "POST":
            form = DevEditPolicyTemplateForm(request.POST)

            if form.is_valid():
                policy.text = form.cleaned_data['text']
                policy.provider = DataProvider.objects.get(path_name=form.cleaned_data['provider'])
                policy.save()
                policy.group.approved = False
                policy.group.save()
                return redirect("/dev/view/group/" + str(policy.group.id))
        else:
            form = DevEditPolicyTemplateForm(initial={"text" : policy.text,
                                                        "provider" : policy.provider.path_name})

        return render(request, 'dev/form.html', {"redirect" : "/dev/edit/policy/template/" + str(policy_id),
                                                    "back" : "/dev/view/group/" + str(policy.group.id),
                                                    "title" : "Edit Policy",
                                                    "form_title" : "Edit Policy",
                                                    "form" : form})
    else:
        return redirect("/dev")
