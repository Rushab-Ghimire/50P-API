import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from salon.models import (
    Variant,
    EntityType,
)
from graphql_jwt.decorators import login_required


class VariantType(DjangoObjectType):
    class Meta:
        model = Variant
        fields = [
            "id",
            "title",
            "sales_price",
            "cost_price",
            "entity_type",
            "entity_id",
        ]


class EntityTypeType(DjangoObjectType):
    class Meta:
        model = EntityType
        fields = ["id", "title"]


class VariantDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(VariantType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_variant = graphene.Field(
        VariantDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_variant_by_id = graphene.Field(VariantType, id=graphene.Int())
    salon_variant_by_entity_type_and_entity_id = graphene.List(
        VariantType,
        entity_type_id=graphene.Int(required=True),
        entity_id=graphene.Int(required=True),
    )

    @login_required
    def resolve_salon_variant(self, info, **kwargs):
        org = info.context.user.get_organization()

        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        qs = Variant.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return VariantDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_salon_variant_by_id(root, info, id):
        org = info.context.user.get_organization()
        return Variant.objects.get(pk=id, organization=org)

    @login_required
    def resolve_salon_variant_by_entity_type_and_entity_id(
        root, info, entity_type_id, entity_id
    ):
        org = info.context.user.get_organization()
        entity_type = EntityType.objects.get(pk=entity_type_id)
        return Variant.objects.filter(
            entity_type=entity_type, entity_id=entity_id, organization=org
        )


class CreateSalonVariant(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        sales_price = graphene.Float()
        cost_price = graphene.Float()
        entity_type_id = graphene.Int(required=True)
        entity_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    variant = graphene.Field(VariantType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        entity_type_id = kwargs.get("entity_type_id")
        try:
            entity_type = EntityType.objects.get(id=entity_type_id)
        except EntityType.DoesNotExist:
            raise Exception("Entity type does not exist")

        item = Variant(
            title=kwargs.get("title"),
            sales_price=kwargs.get("sales_price", 0.0),
            cost_price=kwargs.get("cost_price", 0.0),
            entity_type=entity_type,
            entity_id=kwargs.get("entity_id"),
            organization=org,
            user=session_user,
        )
        item.save()
        return CreateSalonVariant(ok=True, variant=item)


class DeleteSalonVariant(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()

        try:
            item = Variant.objects.get(pk=id, organization=org)
        except Variant.DoesNotExist:
            raise Exception("Variant does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonVariant(ok=True)


class UpdateSalonVariant(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        sales_price = graphene.Float()
        cost_price = graphene.Float()
        entity_type_id = graphene.Int()
        entity_id = graphene.Int()

    ok = graphene.Boolean()
    variant = graphene.Field(VariantType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()

        try:
            item = Variant.objects.get(pk=id, organization=org)
        except Variant.DoesNotExist:
            raise Exception("Variant does not exist")

        entity_type_id = kwargs.get("entity_type_id")
        entity = None
        if entity_type_id:
            try:
                entity = EntityType.objects.get(pk=entity_type_id)
            except EntityType.DoesNotExist:
                raise Exception("Entity Type does not exist")

        item.title = kwargs.get("title")
        item.sales_price = kwargs.get("sales_price") or item.sales_price
        item.cost_price = kwargs.get("cost_price") or item.cost_price
        item.entity_type = entity or item.entity_type
        item.entity_id = kwargs.get("entity_id") or item.entity_id
        item.save()
        return UpdateSalonVariant(ok=True, variant=item)


class Mutation(graphene.ObjectType):
    salon_variant_create = CreateSalonVariant.Field()
    salon_variant_update = UpdateSalonVariant.Field()
    salon_variant_delete = DeleteSalonVariant.Field()


schema_salon_variant = graphene.Schema(query=Query, mutation=Mutation)
