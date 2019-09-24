import graphene

import ancile.web.api.schema


class Query(ancile.web.api.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    pass

class Mutations(ancile.web.api.schema.Mutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutations)
