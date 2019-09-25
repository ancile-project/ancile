from ancile.web.api.graphene_models.mutations import *
from ancile.web.api.graphene_models.types import *


class Mutations(graphene.ObjectType):
    # delete
    delete_token = DeleteToken.Field()
    delete_app = DeleteApp.Field()

    # add
    add_permission_group = AddPermissionGroup.Field()
    add_app = AddApp.Field()
    add_provider = AddProvider.Field()

    # create
    create_permission_group = CreatePermissionGroup.Field()


class Query(object):
    all_providers = graphene.List(ProviderType)
    all_scopes = graphene.List(ScopeType)
    all_tokens = graphene.List(TokenType)
    all_apps = graphene.List(AppType)
    all_policies = graphene.List(PolicyType)

    developer_apps = graphene.List(AppType, id=graphene.Int(default_value=-1))
    current_user = graphene.Field(UserType)

    def resolve_all_providers(self, info, **args):
        return models.DataProvider.objects.all()
    
    def resolve_all_scopes(self, info, **args):
        return models.Scope.objects.all()
    
    def resolve_all_tokens(self, info, **args):
        return models.Token.objects.filter(user=info.context.user)
    
    def resolve_all_apps(self, info, **args):
        return models.App.objects.all()
    
    def resolve_developer_apps(self, info, id, **args):
        if info.context.user.is_developer:
            if id < 0:
                return models.App.objects.filter(developers=info.context.user)
        return models.App.objects.filter(id=id, developers=info.context.user)

    def resolve_current_user(self, info, **args):
        return info.context.user

    def resolve_all_policies(self, info, **args):
        return models.Policy.objects.all()