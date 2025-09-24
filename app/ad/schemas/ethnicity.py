import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Ethnicity
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required


class EthnicityType(DjangoObjectType):
    class Meta:
        model = Ethnicity
        fields = ["id", "title"]


class EthnicityDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(EthnicityType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    ethnicities = graphene.Field(
        EthnicityDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    ethnicity_by_id = graphene.Field(EthnicityType, id=graphene.Int())

    def resolve_ethnicities(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        qs = Ethnicity.objects.filter(filter)
        qs = qs.order_by("-title")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return EthnicityDataModelType(totalCount=totalCount, rows=qs)

    def resolve_ethnicity_by_id(self, info, id):
        return Ethnicity.objects.get(pk=id)


class CreateEthnicity(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)

    ethnicity = graphene.Field(EthnicityType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user

        ethnicity = Ethnicity.objects.create(
            title=kwargs.get("title"),
            organization=session_user.get_organization(),
            user=session_user,
        )
        return CreateEthnicity(ethnicity=ethnicity)


class UpdateEthnicity(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()

    Ethnicity = graphene.Field(EthnicityType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = Ethnicity.objects.get(pk=id)
        except Ethnicity.DoesNotExist:
            raise ValidationError("Ethnicity does not exist")

        item.title = kwargs.get("title", item.title)

        item.save(
            update_fields=[
                "title",
            ]
        )
        return UpdateEthnicity(Ethnicity=item)


class DeleteEthnicity(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        item = Ethnicity.objects.get(pk=id, user=info.context.user)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteEthnicity(ok=True)


class Mutation(graphene.ObjectType):
    ethnicity_add = CreateEthnicity.Field()
    ethnicity_update = UpdateEthnicity.Field()
    ethnicity_delete = DeleteEthnicity.Field()


ethnicity_schema = graphene.Schema(query=Query, mutation=Mutation)
