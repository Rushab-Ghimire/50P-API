import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from salon.models import (
    Category,
    EntityType,
)
from organization.models import Organization
from django.conf import settings
from graphql_jwt.decorators import login_required


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ["id", "title", "entity_type"]


class EntityTypeType(DjangoObjectType):
    class Meta:
        model = EntityType
        fields = ["id", "title"]


class CategoryDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(CategoryType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_category = graphene.Field(
        CategoryDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_category_by_id = graphene.Field(CategoryType, id=graphene.Int())
    salon_category_by_entity_type = graphene.List(CategoryType, entity_type_id=graphene.Int())

    @login_required
    def resolve_salon_category(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        qs = Category.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return CategoryDataModelType(totalCount=totalCount, rows=qs)

    def resolve_salon_category_by_id(root, info, id):
        return Category.objects.get(pk=id)

    def resolve_salon_category_by_entity_type(root, info, entity_type_id):
        return Category.objects.filter(entity_type_id=entity_type_id)


class CreateSalonCategory(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        entity_type_id = graphene.Int()

    ok = graphene.Boolean()
    category = graphene.Field(CategoryType)

    @login_required
    def mutate(self, info, title, entity_type_id):
        session_user = info.context.user
        org = session_user.get_organization()

        try:
            entity_type = EntityType.objects.get(id=entity_type_id, organization=org)
        except EntityType.DoesNotExist:
            raise Exception("Entity type does not exist")

        item = Category(title=title, entity_type=entity_type, organization=org, user=session_user)
        item.save()
        return CreateSalonCategory(ok=True, category=item)


class DeleteSalonCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        session_user = info.context.user
        org = session_user.get_organization()

        try:
            item = Category.objects.get(pk=id, organization=org)
        except Category.DoesNotExist:
            raise Exception("Category does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonCategory(ok=True)


class UpdateSalonCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        title = graphene.String()
        entity_type_id = graphene.Int()

    ok = graphene.Boolean()
    category = graphene.Field(CategoryType)

    @login_required
    def mutate(self, info, id, title, entity_type_id):
        session_user = info.context.user
        org = session_user.get_organization()

        try:
            item = Category.objects.get(pk=id, organization=org)
        except Category.DoesNotExist:
            raise Exception("Category does not exist")

        try:
            entity = EntityType.objects.get(pk=entity_type_id, organization=org)
        except EntityType.DoesNotExist:
            raise Exception("Entity Type does not exist")

        item.title = title
        item.entity_type = entity
        item.save()
        return UpdateSalonCategory(ok=True, category=item)


class Mutation(graphene.ObjectType):
    salon_category_create = CreateSalonCategory.Field()
    salon_category_update = UpdateSalonCategory.Field()
    salon_category_delete = DeleteSalonCategory.Field()


schema_salon_category = graphene.Schema(query=Query, mutation=Mutation)
