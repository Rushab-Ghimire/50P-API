import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Specialization, SpecializationCategory
from django.core.exceptions import ValidationError
from ad.schemas.micro_tasks import ADSelectorDataModelType

class SpecializationType(DjangoObjectType):
    class Meta:
        model = Specialization
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "specialization_category",
        ]


class SpecializationDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(SpecializationType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    all_specializations_for_dropdown = graphene.Field(
        ADSelectorDataModelType
    )
    all_specializations = graphene.Field(
        SpecializationDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
        category_id=graphene.Int()
    )
    specialization_by_id = graphene.Field(SpecializationType, id=graphene.Int())

    def resolve_all_specializations_for_dropdown(self, info, **kwargs):
        qs_cat = SpecializationCategory.objects.all()
        DS = []
        for cat in qs_cat:
            DS_Item = {"category": cat.title, "specializations": list(
                cat.specialization_set.all().values("id", "title")
            )}
            DS.append(DS_Item)
        return ADSelectorDataModelType(totalCount=1, rows=DS)

    def resolve_all_specializations(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        category_id = kwargs.get("category_id")

        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        if category_id:
            filter &= Q(specialization_category_id=category_id)

        qs = Specialization.objects.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return SpecializationDataModelType(totalCount=totalCount, rows=qs)

    def resolve_specialization_by_id(self, info, id):
        try:
            return Specialization.objects.get(pk=id)
        except Specialization.DoesNotExist:
            return None


class CreateSpecialization(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        category_id = graphene.Int()

    specialization = graphene.Field(SpecializationType)

    def mutate(self, info, **kwargs):
        title = kwargs.get("title")
        description = kwargs.get("description")
        category_id = kwargs.get("category_id")

        category = None
        if category_id:
            try:
                category = SpecializationCategory.objects.get(pk=category_id)
            except SpecializationCategory.DoesNotExist:
                raise ValidationError("Category not found")

        slug = Specialization.generate_slug(title)
        specialization = Specialization.objects.create(
            title=title,
            slug=slug,
            description=description,
            specialization_category=category,
        )
        return CreateSpecialization(specialization=specialization)


class UpdateSpecialization(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        slug = graphene.String()
        description = graphene.String()
        category_id = graphene.Int()

    specialization = graphene.Field(SpecializationType)

    def mutate(self, info, id, **kwargs):
        title = kwargs.get("title")
        slug = kwargs.get("slug")
        description = kwargs.get("description")
        category_id = kwargs.get("category_id")

        try:
            specialization = Specialization.objects.get(pk=id)
        except Specialization.DoesNotExist:
            raise ValidationError("Specialization not found")

        if category_id:
            try:
                category = SpecializationCategory.objects.get(pk=category_id)
                specialization.specialization_category = category
            except SpecializationCategory.DoesNotExist:
                raise ValidationError("Category not found")

        specialization.title = title or specialization.title
        if slug:
            specialization.slug = Specialization.generate_slug(slug)
        specialization.description = description or specialization.description

        specialization.save()
        return UpdateSpecialization(specialization=specialization)


class DeleteSpecialization(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            specialization = Specialization.objects.get(pk=id)
        except Specialization.DoesNotExist:
            raise ValidationError("Specialization not found")

        specialization.is_deleted = True
        specialization.save()
        return DeleteSpecialization(ok=True)


class Mutation(graphene.ObjectType):
    specialization_create = CreateSpecialization.Field()
    specialization_update = UpdateSpecialization.Field()
    specialization_delete = DeleteSpecialization.Field()


specialization_schema = graphene.Schema(query=Query, mutation=Mutation)
