import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import InsuranceProvider, ADUserFileTypes
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required
from core.utils.tf_utils import get_ad_file_URL_by_unique_id


class InsuranceProviderType(DjangoObjectType):
    logoUuid = graphene.String()

    class Meta:
        model = InsuranceProvider
        fields = ["id", "name", "logo", "location"]

    def resolve_logoUuid(self, info):
        return self.logo

    def resolve_logo(self, info):
        return get_ad_file_URL_by_unique_id(self.logo, ADUserFileTypes.MEDIA)


class InsuranceProviderDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(InsuranceProviderType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    insurance_provider = graphene.Field(
        InsuranceProviderDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    insurance_provider_by_id = graphene.Field(InsuranceProviderType, id=graphene.Int())

    def resolve_insurance_provider(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            filter = Q(name__icontains=search)

        qs = InsuranceProvider.objects.filter(filter)
        qs = qs.order_by("-created_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return InsuranceProviderDataModelType(totalCount=totalCount, rows=qs)

    def resolve_insurance_provider_by_id(self, info, id):
        return InsuranceProvider.objects.get(pk=id)


class CreateInsuranceProvider(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        logo = graphene.String()
        location = graphene.String()

    insurance_provider = graphene.Field(InsuranceProviderType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user

        insurance_provider = InsuranceProvider.objects.create(
            name=kwargs.get("name"),
            logo=kwargs.get("logo"),
            location=kwargs.get("location"),
            organization=session_user.get_organization(),
            user=session_user,
        )
        return CreateInsuranceProvider(insurance_provider=insurance_provider)


class UpdateInsuranceProvider(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        logo = graphene.String()
        location = graphene.String()

    InsuranceProvider = graphene.Field(InsuranceProviderType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = InsuranceProvider.objects.get(pk=id, user=info.context.user)
        except InsuranceProvider.DoesNotExist:
            raise ValidationError("Insurance provider does not exist")

        item.name = kwargs.get("name", item.name)
        item.logo = kwargs.get("logo", item.logo)
        item.location = kwargs.get("location", item.location)

        item.save(
            update_fields=[
                "name",
                "logo",
                "location",
            ]
        )
        return UpdateInsuranceProvider(InsuranceProvider=item)


class DeleteInsuranceProvider(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        item = InsuranceProvider.objects.get(pk=id, user=info.context.user)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteInsuranceProvider(ok=True)


class Mutation(graphene.ObjectType):
    insurance_provider_add = CreateInsuranceProvider.Field()
    insurance_provider_update = UpdateInsuranceProvider.Field()
    insurance_provider_delete = DeleteInsuranceProvider.Field()


insurance_provider_schema = graphene.Schema(query=Query, mutation=Mutation)
