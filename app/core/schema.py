import graphene
import graphql_jwt

import ad.schemas.student as student

class Query(
            student.student_schema.Query,
            graphene.ObjectType):
    # Inherits all classes and methods from app-specific queries, so no need
    # to include additional code here.
    pass

class Mutation(
               student.student_schema.Mutation,
               graphene.ObjectType):
    # Inherits all classes and methods from app-specific mutations, so no need
    # to include additional code here.
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
