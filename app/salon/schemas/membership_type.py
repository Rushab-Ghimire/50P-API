import graphene
from graphene_django import DjangoObjectType
from salon.models import (
    MembershipType,
)
from organization.models import Organization
from django.conf import settings
from django.db.models import Q
from graphql_jwt.decorators import login_required


class MembershipTypeType(DjangoObjectType):
    class Meta:
        model = MembershipType
        fields = ["id", "title", "fee", "billing_period", "organization"]


class OrganizationType(DjangoObjectType):
    class Meta:
        model = Organization
        fields = ["id", "name"]


class MembershipTypeDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(MembershipTypeType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_all_membership_type = graphene.Field(
        MembershipTypeDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_membership_type_by_id = graphene.Field(MembershipTypeType, id=graphene.Int())

    @login_required
    def resolve_salon_all_membership_type(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        org = info.context.user.get_organization()

        qs = MembershipType.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return MembershipTypeDataModelType(totalCount=totalCount, rows=qs)

    def resolve_salon_membership_type_by_id(root, info, id):
        return MembershipType.objects.get(pk=id)


class CreateSalonMembershipType(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        fee = graphene.Float()
        billing_period = graphene.Int()

    ok = graphene.Boolean()
    membership_type = graphene.Field(MembershipTypeType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        item = MembershipType(
            title=kwargs.get("title"),
            fee=kwargs.get("fee"),
            billing_period=kwargs.get("billing_period"),
            organization=org,
            user=session_user,
        )

        item.save()
        return CreateSalonMembershipType(ok=True, membership_type=item)


class DeleteSalonMembershipType(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()
        try:
            item = MembershipType.objects.get(pk=id, organization=org)
        except MembershipType.DoesNotExist:
            raise Exception("Membership Type does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonMembershipType(ok=True)


class UpdateSalonMembershipType(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        title = graphene.String()
        fee = graphene.Float()
        billing_period = graphene.Int()

    ok = graphene.Boolean()
    membership_type = graphene.Field(MembershipTypeType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()
        try:
            item = MembershipType.objects.get(pk=id, organization=org)
        except MembershipType.DoesNotExist:
            raise Exception("Membership Type does not exist")

        item.title = kwargs.get("title") or item.title
        item.fee = kwargs.get("fee") or item.fee
        item.billing_period = kwargs.get("billing_period") or item.billing_period
        item.save()
        return UpdateSalonMembershipType(ok=True, membership_type=item)


class Mutation(graphene.ObjectType):
    salon_membership_type_create = CreateSalonMembershipType.Field()
    salon_membership_type_update = UpdateSalonMembershipType.Field()
    salon_membership_type_delete = DeleteSalonMembershipType.Field()


schema_salon_membership_type = graphene.Schema(query=Query, mutation=Mutation)
