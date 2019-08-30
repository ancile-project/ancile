import graphene
from graphene_django.types import DjangoObjectType
from ancile.web.dashboard import models

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

class Mutations(graphene.ObjectType):
    delete_token = DeleteToken.Field()

class Query(object):
    all_providers = graphene.List(ProviderType)
    all_scopes = graphene.List(ScopeType)
    all_tokens = graphene.List(TokenType)
    
    def resolve_all_providers(self, info, **args):
        return models.DataProvider.objects.all()
    
    def resolve_all_scopes(self, info, **args):
        return models.Scope.objects.all()
    
    def resolve_all_tokens(self, info, **args):
        return models.Token.objects.filter(user=info.context.user)
