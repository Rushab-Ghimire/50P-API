import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import SpecializationCategory, MedicalTypes
from django.core.exceptions import ValidationError


class SpecializationCategoryType(DjangoObjectType):
    class Meta:
        model = SpecializationCategory
        fields = ["id", "title", "slug", "medical_type"]


class SpecializationCategoryDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(SpecializationCategoryType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    all_specialization_category = graphene.Field(
        SpecializationCategoryDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    specialization_category_by_id = graphene.Field(SpecializationCategoryType, id=graphene.Int())

    def resolve_all_specialization_category(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        qs = SpecializationCategory.objects.filter(filter)
        qs = qs.order_by("-modified_date")

        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]



        return SpecializationCategoryDataModelType(totalCount=totalCount, rows=qs)

    def resolve_specialization_category_by_id(self, info, id):
        try:
            return SpecializationCategory.objects.get(pk=id)
        except SpecializationCategory.DoesNotExist:
            return None


class CreateSpecializationCategory(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        medical_type = graphene.String()

    specialization_category = graphene.Field(SpecializationCategoryType)

    def mutate(self, info, title, medical_type=None):
        if medical_type:
            medical_type = medical_type.lower()
            if medical_type not in MedicalTypes.values:
                raise ValidationError("Invalid medical type")

        slug = SpecializationCategory.generate_slug(title)
        specialization_category = SpecializationCategory.objects.create(
            title=title, slug=slug, medical_type=medical_type
        )
        return CreateSpecializationCategory(specialization_category=specialization_category)


class UpdateSpecializationCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        slug = graphene.String()
        medical_type = graphene.String()

    specialization_category = graphene.Field(SpecializationCategoryType)

    def mutate(self, info, id, **kwargs):
        title = kwargs.get("title")
        slug = kwargs.get("slug")
        medical_type = kwargs.get("medical_type")

        try:
            specialization_category = SpecializationCategory.objects.get(pk=id)
        except SpecializationCategory.DoesNotExist:
            raise ValidationError("SpecializationCategory not found")

        if medical_type:
            medical_type = medical_type.lower()
            if medical_type not in MedicalTypes.values:
                raise ValidationError("Invalid medical type")
            specialization_category.medical_type = medical_type

        specialization_category.title = title or specialization_category.title
        if slug and slug.strip() != "":
            specialization_category.slug = SpecializationCategory.generate_slug(slug)

        specialization_category.save()
        return UpdateSpecializationCategory(specialization_category=specialization_category)


class DeleteSpecializationCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            specialization_category = SpecializationCategory.objects.get(pk=id)
        except SpecializationCategory.DoesNotExist:
            raise ValidationError("SpecializationCategory not found")

        specialization_category.is_deleted = True
        specialization_category.save()
        return DeleteSpecializationCategory(ok=True)


class Mutation(graphene.ObjectType):
    specialization_category_create = CreateSpecializationCategory.Field()
    specialization_category_update = UpdateSpecializationCategory.Field()
    specialization_category_delete = DeleteSpecializationCategory.Field()


specialization_category_schema = graphene.Schema(query=Query, mutation=Mutation)
