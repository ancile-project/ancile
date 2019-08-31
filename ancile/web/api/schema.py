import graphene
from graphene_django.types import DjangoObjectType
from ancile.web.dashboard import models
from ancile.web.api.visualizer import parse_policy

class ScopeType(DjangoObjectType):
    class Meta:
        model = models.Scope

class ProviderType(DjangoObjectType):
    scopes = graphene.List(ScopeType)
    
    class Meta:
        model = models.DataProvider
        exclude_fields = ('clientId', 'clientSecret', 'accessTokenUrl', 'authUrl')

    def resolve_scopes(self, info, **args):
        return models.Scope.objects.filter(provider=self)

class TokenType(DjangoObjectType):
    
    class Meta:
        model = models.Token
        
class DeleteToken(graphene.Mutation):
    class Arguments:
        token = graphene.Int()
    
    ok = graphene.Boolean()
    
    def mutate(root, info, token):
        token = models.Token.objects.get(id=token)
        token.delete()
        return DeleteToken(ok=True)

class PolicyType(DjangoObjectType):
    
    graph = graphene.String()
    
    class Meta:
        model = models.Policy
        only_fields = ('provider', 'text')
        
    def resolve_graph(self, info, **args):
        return parse_policy(self.text)

class PermissionGroupType(DjangoObjectType):
    
    class Meta:
        model = models.PermissionGroup
        only_fields = ("id", "name", "description", "scopes", )
    
    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(approved=True)

class AppType(DjangoObjectType):
    
    policies = graphene.List(PolicyType)
    groups = graphene.List(PermissionGroupType)
    
    class Meta:
        model = models.App
        only_fields = ('id', 'name', 'description')
    
    def resolve_policies(self, info, **args):
        policies = models.Policy.objects.filter(user=info.context.user, app=self)
        return policies
    
    def resolve_groups(self, info, **args):
        permission_groups = models.PermissionGroup.objects.filter(app=self)
        return permission_groups

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

class Mutations(graphene.ObjectType):
    delete_token = DeleteToken.Field()
    delete_app = DeleteApp.Field()
    add_permission_group = AddPermissionGroup.Field()

class Query(object):
    all_providers = graphene.List(ProviderType)
    all_scopes = graphene.List(ScopeType)
    all_tokens = graphene.List(TokenType)
    all_apps = graphene.List(AppType)
    
    def resolve_all_providers(self, info, **args):
        return models.DataProvider.objects.all()
    
    def resolve_all_scopes(self, info, **args):
        return models.Scope.objects.all()
    
    def resolve_all_tokens(self, info, **args):
        return models.Token.objects.filter(user=info.context.user)
    
    def resolve_all_apps(self, info, **args):
        return models.App.objects.all()
