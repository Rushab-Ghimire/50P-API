import graphene
from graphene_django import DjangoObjectType
from salon.models import (
    CustomerSalon, Media, UserFile
)
from organization.models import Organization
from django.conf import settings
from django.db.models import Q
from core.utils.tf_utils import get_file_URL_by_unique_id, get_user_file_URL, get_customer_file_URL
from graphql_jwt.decorators import login_required


class CustomerSalonType(DjangoObjectType):
    profile_pic = graphene.String()
    class Meta:
        model = CustomerSalon
        fields = ["id", "first_name", "last_name", "email", "phone", "organization"]

    def resolve_profile_pic(self, info):
        return self.profile_pic()


class OrganizationType(DjangoObjectType):
    class Meta:
        model = Organization
        fields = ["id", "name"]


class CustomerSalonDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(CustomerSalonType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_customer = graphene.Field(
        CustomerSalonDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_customer_by_id = graphene.Field(CustomerSalonType, id=graphene.Int())
    salon_media = graphene.Field(graphene.String(),
                                 owner_id=graphene.Int(),
                                 owner_type=graphene.String(),
                                 key=graphene.String())
    salon_media_by_unique_id = graphene.Field(graphene.String(),
                                 unique_id=graphene.String())

    @login_required
    def resolve_salon_customer(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = (
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        org = info.context.user.get_organization()

        qs = CustomerSalon.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return CustomerSalonDataModelType(totalCount=totalCount, rows=qs)

    def resolve_salon_customer_by_id(root, info, id):
        return CustomerSalon.objects.get(pk=id)

    def resolve_salon_media(root, info, owner_id, owner_type, key):
        if owner_type.lower() == "customer":
            return get_customer_file_URL(owner_id, key, "media")
        if owner_type.lower() == "user":
            return get_user_file_URL(owner_id, key, "media")

    def resolve_salon_media_by_unique_id(root, info, unique_id):
        return get_file_URL_by_unique_id(unique_id, "media")



class CreateSalonCustomer(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)
        unique_id=graphene.String(required=False)

    ok = graphene.Boolean()
    customer = graphene.Field(CustomerSalonType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        item = CustomerSalon(
            first_name=kwargs.get("first_name"),
            last_name=kwargs.get("last_name"),
            email=kwargs.get("email"),
            phone=kwargs.get("phone"),
            organization=org,
            user=session_user,
        )
        item.save()

        unique_id = kwargs.get("unique_id")
        if unique_id != "":
            uf = UserFile(
                key = "PROFILE_IMAGE",
                unique_id = unique_id,
                customer = item,
                organization=org,
                user=session_user,
            )
            uf.save()
        return CreateSalonCustomer(ok=True, customer=item)


class DeleteSalonCustomer(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()
        try:
            item = CustomerSalon.objects.get(pk=id, organization=org)
        except CustomerSalon.DoesNotExist:
            raise Exception("Customer does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonCustomer(ok=True)


class UpdateSalonCustomer(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        unique_id=graphene.String(required=False)

    ok = graphene.Boolean()
    customer = graphene.Field(CustomerSalonType)

    @login_required
    def mutate(self, info, id, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        try:
            item = CustomerSalon.objects.get(pk=id, organization=org)
        except CustomerSalon.DoesNotExist:
            raise Exception("Customer does not exist")

        item.first_name = kwargs.get("first_name") or item.first_name
        item.last_name = kwargs.get("last_name") or item.last_name
        item.email = kwargs.get("email") or item.email
        item.phone = kwargs.get("phone") or item.phone
        item.save()

        unique_id = kwargs.get("unique_id", "")
        if unique_id != "":
            uf = UserFile.objects.filter(key = "PROFILE_IMAGE", customer = item).first()
            if uf:
                uf.unique_id = unique_id
                uf.save()
            else:
                uf = UserFile(
                        key = "PROFILE_IMAGE",
                        unique_id=unique_id,
                        customer=item,
                        organization=org,
                        user=session_user,
                    )
                uf.save()



        return UpdateSalonCustomer(ok=True, customer=item)


class Mutation(graphene.ObjectType):
    salon_customer_create = CreateSalonCustomer.Field()
    salon_customer_update = UpdateSalonCustomer.Field()
    salon_customer_delete = DeleteSalonCustomer.Field()


schema_salon_customer = graphene.Schema(query=Query, mutation=Mutation)
