import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Gender
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required


class GenderType(DjangoObjectType):
    class Meta:
        model = Gender
        fields = ["id", "title"]


class GenderDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(GenderType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    genders = graphene.Field(
        GenderDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    gender_by_id = graphene.Field(GenderType, id=graphene.Int())

    def resolve_genders(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        qs = Gender.objects.filter(filter)
        qs = qs.order_by("-title")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return GenderDataModelType(totalCount=totalCount, rows=qs)

    def resolve_gender_by_id(self, info, id):
        return Gender.objects.get(pk=id)


class CreateGender(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)

    gender = graphene.Field(GenderType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user

        gender = Gender.objects.create(
            title=kwargs.get("title"),
            organization=session_user.get_organization(),
            user=session_user,
        )
        return CreateGender(gender=gender)


class UpdateGender(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()

    Gender = graphene.Field(GenderType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = Gender.objects.get(pk=id)
        except Gender.DoesNotExist:
            raise ValidationError("Gender does not exist")

        item.title = kwargs.get("title", item.title)

        item.save(
            update_fields=[
                "title",
            ]
        )
        return UpdateGender(Gender=item)


class DeleteGender(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        item = Gender.objects.get(pk=id, user=info.context.user)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteGender(ok=True)


class Mutation(graphene.ObjectType):
    gender_add = CreateGender.Field()
    gender_update = UpdateGender.Field()
    gender_delete = DeleteGender.Field()


gender_schema = graphene.Schema(query=Query, mutation=Mutation)
