import graphene
from ancile.web.dashboard import models

class DeleteToken(graphene.Mutation):
    class Arguments:
        token = graphene.Int()

    ok = graphene.Boolean()

    def mutate(root, info, token):
        token = models.Token.objects.get(id=token)
        token.delete()
        return DeleteToken(ok=True)

class DeleteApp(graphene.Mutation):
    class Arguments:
        app = graphene.Int()

    ok = graphene.Boolean()

    def mutate(root, info, app):
        models.Policy.objects.filter(app__id=app, user=info.context.user).delete()
        return DeleteApp(ok=True)


class AddPermissionGroup(graphene.Mutation):
    class Arguments:
        app = graphene.Int()
        group = graphene.Int()

    ok = graphene.Boolean()

    def mutate(root, info, group, app):
        app = models.App.objects.get(id=app)
        perm_group = models.PermissionGroup.objects.get(id=group, app=app)

        needed_policies = models.PolicyTemplate.objects.filter(group=perm_group,
                                                               app=app)

        new_policies = []

        for policy in needed_policies:
            if not models.Token.objects.filter(provider=policy.provider):
                raise Exception("Provider not found")

            new_policy = models.Policy(
                text=policy.text,
                provider=policy.provider,
                user=info.context.user,
                app=app,
                active=True
            )

            new_policies.append(new_policy)

        for policy in new_policies:
            policy.save()

        return AddPermissionGroup(ok=True)


class CreatePermissionGroup(graphene.Mutation):
    class Arguments:
        app = graphene.Int()
        name = graphene.String()
        description = graphene.String()
        approved = graphene.Boolean(default_value=False)

    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, approved, description, name, app):
        try:
            app = models.App.objects.get(id=app)
        except models.app.DoesNotExist:
            return CreatePermissionGroup(ok=False, error="App not found")

        approved = approved if info.context.user.is_superuser else False

        if info.context.user.is_superuser or (info.context.user.is_developer and info.context.user in app.developers):
            if name and description:
                group = models.PermissionGroup(name=name,
                                               description=description,
                                               app=app,
                                               approved=approved)
                group.save()
                return CreatePermissionGroup(ok=True)
            return CreatePermissionGroup(ok=False, error="Name and/or description missing")
        return CreatePermissionGroup(ok=False, error="Insufficient permissions")


class AddApp(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String()

    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(root, info, name, description):
        if info.context.user.is_developer:
            if not models.App.objects.filter(name=name):
                app = models.App(name=name, description=description)
                app.save()
                app.developers.add(info.context.user)
                return AddApp(ok=True)
            return AddApp(ok=False, error="App with same name already exists")
        return AddApp(ok=False, error="Insufficient privileges")


class AddProvider(graphene.Mutation):
    class Arguments:
        provider_type = graphene.String()
        path_name = graphene.String()
        display_name = graphene.String()
        client_id = graphene.String()
        client_secret = graphene.String()
        access_token_url = graphene.String()
        auth_url = graphene.String()
        extra_params = graphene.String()

    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(root, info, oauth_type, path_name, display_name, provider_type,
               client_id=None, client_secret=None, access_token_url=None,
               auth_url=None):
        if info.context.user.is_superuser:
            if not models.DataProvider.objects.filter(display_name=display_name):
                provider = models.DataProvider(oauth_type, path_name, display_name, provider_type,
                   client_id, client_secret, access_token_url,auth_url)
                provider.save()
                return AddProvider(ok=True)
            return AddProvider(ok=False, error="DataProvider with same name already exists")
        return AddProvider(ok=False, error="Insufficient privileges")

