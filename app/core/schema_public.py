import graphene


import authtf.schema_invitation as schema_invitation


class Query(
            schema_invitation.schema_invitation.Query,
            graphene.ObjectType):
    # Inherits all classes and methods from app-specific queries, so no need
    # to include additional code here.
    pass

class Mutation(graphene.ObjectType):
    # Inherits all classes and methods from app-specific mutations, so no need
    # to include additional code here.
    pass


schema_public = graphene.Schema(query=Query)