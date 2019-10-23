import graphene
from graphene_django.types import DjangoObjectType
from ancile.web.dashboard import models
from ancile.web.api.visualizer import parse_policy


class UserType(DjangoObjectType):
    class Meta:
        model = models.User
        only_fields = ('username', 'first_name', 'last_name', 'email', 'is_superuser',
                        'is_pending_developer')
    
    is_developer = graphene.Boolean()
    
    def resolve_is_developer(self, info, **args):
        return self.is_developer


class ScopeType(DjangoObjectType):
    class Meta:
        model = models.Scope


class TokenType(DjangoObjectType):
    class Meta:
        model = models.Token
        only_fields = ('id', 'provider', 'expires_at', 'scopes',)


class ProviderType(DjangoObjectType):
    scopes = graphene.List(ScopeType)
    token = graphene.Field(TokenType)

    class Meta:
        model = models.DataProvider
        exclude_fields = ('clientId', 'clientSecret', 'accessTokenUrl', 'authUrl')

    def resolve_scopes(self, info, **args):
        return models.Scope.objects.filter(provider=self)

    def resolve_token(self, info, **args):
        return models.Token.objects.filter(provider=self, user=info.context.user).first()


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
        only_fields = ("id", "name", "description", "scopes",)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(approved=True)

class AppType(DjangoObjectType):
    policies = graphene.List(PolicyType)
    groups = graphene.List(PermissionGroupType)
    token = graphene.String()

    class Meta:
        model = models.App
        only_fields = ('id', 'name', 'description', 'developers',)

    def resolve_policies(self, info, **args):
        policies = models.Policy.objects.filter(user=info.context.user, app=self)
        return policies

    def resolve_groups(self, info, **args):
        permission_groups = models.PermissionGroup.objects.filter(app=self)
        return permission_groups

    def resolve_developers(self, info, **args):
        if info.context.user.is_developer:
            return self.developers

    def resolve_token(self, info, **args):
        if info.context.user.is_developer:
            return self.encoded_salt
