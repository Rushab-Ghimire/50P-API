import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Clinic
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required


class ClinicType(DjangoObjectType):
    class Meta:
        model = Clinic
        fields = ["id", "title", "address"]


class ClinicDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(ClinicType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    clinic = graphene.Field(
        ClinicDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    clinic_by_id = graphene.Field(ClinicType, id=graphene.Int())

    def resolve_clinic(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q(user=info.context.user)
        if search:
            filter = Q(title__icontains=search)

        qs = Clinic.objects.filter(filter)
        qs = qs.order_by("-title")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return ClinicDataModelType(totalCount=totalCount, rows=qs)

    def resolve_clinic_by_id(self, info, id):
        try:
            return Clinic.objects.get(pk=id)
        except Clinic.DoesNotExist:
            return None


class CreateClinic(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        address = graphene.String()

    clinic = graphene.Field(ClinicType)

    def mutate(self, info, title, address=None):
        clinic = Clinic.objects.create(
            title=title,
            address=address,
            user=info.context.user,
        )
        return CreateClinic(clinic=clinic)


class UpdateClinic(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        address = graphene.String()

    Clinic = graphene.Field(ClinicType)

    def mutate(self, info, id, **kwargs):
        try:
            item = Clinic.objects.get(pk=id)
        except Clinic.DoesNotExist:
            raise ValidationError("Clinic does not exist")

        item.title = kwargs.get("title", item.title)
        item.address = kwargs.get("address", item.address)

        item.save(
            update_fields=[
                "title",
                "address",
            ]
        )
        return UpdateClinic(Clinic=item)


class DeleteClinic(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    def mutate(self, info, id):
        try:
            item = Clinic.objects.get(pk=id)
        except Clinic.DoesNotExist:
            raise ValidationError("Clinic does not exist")

        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteClinic(ok=True)


class Mutation(graphene.ObjectType):
    clinic_add = CreateClinic.Field()
    clinic_update = UpdateClinic.Field()
    clinic_delete = DeleteClinic.Field()


clinic_schema = graphene.Schema(query=Query, mutation=Mutation)
