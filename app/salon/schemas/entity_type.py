import graphene
from graphene_django import DjangoObjectType
from salon.models import (
    EntityType,
)
from graphql_jwt.decorators import login_required

class EntityTypeType(DjangoObjectType):
    class Meta:
        model = EntityType
        fields = ["id", "title"]


class Query(graphene.ObjectType):
    salon_entity_type = graphene.List(EntityTypeType)

    @login_required
    def resolve_salon_entity_type(self, info, **kwargs):
        org = info.context.user.get_organization()

        return EntityType.objects.filter(organization=org)

schema_entity_type = graphene.Schema(query=Query)
