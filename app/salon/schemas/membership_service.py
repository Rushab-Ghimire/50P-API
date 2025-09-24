import graphene
from graphene_django import DjangoObjectType
from salon.models import MembershipService, MembershipType, Service, Variant
from organization.models import Organization
from django.conf import settings
from django.db.models import Q
from graphql_jwt.decorators import login_required


class MembershipServiceType(DjangoObjectType):
    class Meta:
        model = MembershipService
        fields = [
            "id",
            "membership_type",
            "service",
            "variant",
        ]


class MembershipTypeType(DjangoObjectType):
    class Meta:
        model = MembershipType
        fields = ["id", "title", "fee", "billing_period"]


class ServiceType(DjangoObjectType):
    class Meta:
        model = Service
        fields = ["id", "title", "code", "sales_price", "cost_price", "category"]


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


class MembershipServiceDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(MembershipServiceType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_membership_service = graphene.Field(
        MembershipServiceDataModelType,
        # search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_membership_service_by_id = graphene.Field(MembershipServiceType, id=graphene.Int())

    @login_required
    def resolve_salon_membership_service(self, info, **kwargs):
        # search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        # filter = Q()
        # if search:
        #     filter = Q(title__icontains=search)

        org = info.context.user.get_organization()

        qs = MembershipService.objects.filter(organization=org)
        # qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return MembershipServiceDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_salon_membership_service_by_id(root, info, id):
        org = info.context.user.get_organization()
        return MembershipService.objects.get(pk=id, organization=org)


class CreateSalonMembershipService(graphene.Mutation):
    class Arguments:
        membership_type_id = graphene.Int(required=True)
        service_id = graphene.Int(required=True)
        variant_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    membership_service = graphene.Field(MembershipServiceType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        membership_type_id = kwargs.get("membership_type_id")
        try:
            membership_type = MembershipType.objects.get(pk=membership_type_id, organization=org)
        except MembershipType.DoesNotExist:
            raise Exception("Membership Type does not exists")

        service_id = kwargs.get("service_id")
        try:
            service = Service.objects.get(pk=service_id, organization=org)
        except Service.DoesNotExist:
            raise Exception("Service does not exists")

        variant_id = kwargs.get("variant_id")
        try:
            variant = Variant.objects.get(
                pk=variant_id, organization=org
            )
        except Variant.DoesNotExist:
            raise Exception("Variant does not exists")

        item = MembershipService(
            membership_type=membership_type,
            service=service,
            variant=variant,
            organization=org,
            user=session_user,
        )

        item.save()
        return CreateSalonMembershipService(ok=True, membership_service=item)


class DeleteSalonMembershipService(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()

        try:
            item = MembershipService.objects.get(pk=id, organization=org)
        except MembershipService.DoesNotExist:
            raise Exception("Membership Service does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonMembershipService(ok=True)


class UpdateSalonMembershipService(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        membership_type_id = graphene.Int()
        service_id = graphene.Int()
        variant_id = graphene.Int()

    ok = graphene.Boolean()
    membership_service = graphene.Field(MembershipServiceType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()

        try:
            item = MembershipService.objects.get(pk=id, organization=org)
        except MembershipService.DoesNotExist:
            raise Exception("Membership service does not exist")

        membership_type_id = kwargs.get("membership_type_id")
        membership_type = None
        if membership_type_id:
            try:
                membership_type = MembershipType.objects.get(pk=membership_type_id, organization=org)
            except MembershipType.DoesNotExist:
                raise Exception("Membership Type does not exists")

        service_id = kwargs.get("service_id")
        service = None
        if service_id:
            try:
                service = Service.objects.get(pk=service_id, organization=org)
            except Service.DoesNotExist:
                raise Exception("Service does not exists")

        variant_id = kwargs.get("variant_id")
        variant = None
        if variant_id:
            try:
                variant = Variant.objects.get(
                    pk=variant_id, organization=org
                )
            except Variant.DoesNotExist:
                raise Exception("Variant does not exists")

        item.membership_type = membership_type or item.membership_type
        item.service = service or item.service
        item.variant = variant or item.variant

        item.save()
        return UpdateSalonMembershipService(ok=True, membership_service=item)


class Mutation(graphene.ObjectType):
    salon_membership_service_create = CreateSalonMembershipService.Field()
    salon_membership_service_update = UpdateSalonMembershipService.Field()
    salon_membership_service_delete = DeleteSalonMembershipService.Field()


schema_salon_membership_service = graphene.Schema(query=Query, mutation=Mutation)
