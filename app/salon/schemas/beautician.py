import graphene
from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from graphene_django import DjangoObjectType
from salon.models import Beautician, UserFile
from authtf.models import User, Role
from salon.gql_helpers import get_gql_organization
from core.utils.email_utils import EmailUtils
from sendgrid.helpers.mail import Content
from graphql_jwt.decorators import login_required


class LinkedUserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class BeauticianType(DjangoObjectType):
    class Meta:
        model = Beautician
        fields = ["id", "phone", "address","linked_user", "organization"]


class BeauticianDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(BeauticianType)

    class Meta:
        fields = ["totalCount", "rows"]


class Query(graphene.ObjectType):
    salon_beautician = graphene.Field(
        BeauticianDataModelType,
        organization_id=graphene.Int(),
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_beautician_by_id = graphene.Field(
        BeauticianType, id=graphene.Int(required=True)
    )

    salon_beautician_by_user_id = graphene.Field(
        BeauticianType, id=graphene.Int(required=True)
    )

    @login_required
    def resolve_salon_beautician(self, info, **kwargs):
        organization_id = kwargs.get("organization_id", None)
        org = get_gql_organization(info.context.user, organization_id)
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if org:
            filter = Q(organization=org)
        if search:
            filter &= Q(linked_user__first_name__icontains=search) | Q(
                phone__icontains=search
            )
        qs = Beautician.objects.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return BeauticianDataModelType(totalCount=totalCount, rows=qs)

    def resolve_salon_beautician_by_id(root, info, id):
        return Beautician.objects.get(pk=id)

    def resolve_salon_beautician_by_user_id(root, info, id):
        linked_user = User.objects.get(pk=id)
        return Beautician.objects.get(linked_user=linked_user)


class CreateSalonBeautician(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        phone = graphene.String()
        address = graphene.String()
        unique_id = graphene.String(required=False)

    ok = graphene.Boolean()
    beautician = graphene.Field(BeauticianType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        email = kwargs.get("email")
        first_name = kwargs.get("first_name", "")
        last_name = kwargs.get("last_name", "")
        phone = kwargs.get("phone")
        address = kwargs.get("address")

        user = User.objects.filter(email=email).first()

        with transaction.atomic():
            if user:
                raise Exception("Beautician with given email already exist.")

            else:
                user = User.objects.create_user(
                    email=email,
                    is_active=True,
                    is_staff=False,
                    first_name=first_name,
                    last_name=last_name,
                    password=phone,
                )

            UserOrganization = apps.get_model("authtf", "UserOrganization")
            user_organization = UserOrganization.objects.create(
                user=user, organization=org
            )
            role = Role.objects.get(identifier="staff")
            user_organization.role.add(role)

            EmailUtils.send(
                "noreply@tileflexai.com",
                user.email,
                "New registration as a Beautician",
                Content(
                    "text/html",
                    f"Hello {user.first_name}, <br/> You are registered on {settings.SYSTEM_NAME} "
                    f"as a Beautician on the organization <b>{org.name}</b>. <br/> "
                    f"Click on the link <a href='{settings.SYSTEM_APP_URL}' target='_blank'>{settings.SYSTEM_APP_URL}</a> "
                    f"to access your account.",
                ),
            )

            item = Beautician.objects.create(
                linked_user=user, phone=phone, address=address, organization=org, user=session_user
            )

            unique_id = kwargs.get("unique_id", None)
            if unique_id:
                UserFile.objects.create(
                    key="PROFILE_IMAGE",
                    unique_id=unique_id,
                    linked_user=item.linked_user,
                    organization=org,
                    user=session_user,
                )
            return CreateSalonBeautician(ok=True, beautician=item)


class DeleteSalonBeautician(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()
        try:
            item = Beautician.objects.get(pk=id)
        except Beautician.DoesNotExist:
            raise Exception("Beautician does not exist")

        if org != item.organization:
            raise Exception("Permission denied")

        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteSalonBeautician(ok=True)


class UpdateSalonBeautician(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        email = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        phone = graphene.String()
        address = graphene.String()
        unique_id = graphene.String(required=False)

    ok = graphene.Boolean()
    beautician = graphene.Field(BeauticianType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()

        try:
            item = Beautician.objects.get(pk=id)
        except Beautician.DoesNotExist:
            raise Exception("Beautician does not exist")

        if org != item.organization:
            raise Exception("Permission denied")

        email = kwargs.get("email")
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        phone = kwargs.get("phone")
        address = kwargs.get("address")

        item.linked_user.first_name = first_name or item.linked_user.first_name
        item.linked_user.last_name = last_name or item.linked_user.last_name
        item.linked_user.email = email or item.linked_user.email
        item.linked_user.save()

        item.phone = phone or item.phone
        item.address = address or item.address
        item.save()

        unique_id = kwargs.get("unique_id", "")
        if unique_id != "":
            uf = UserFile.objects.filter(
                key="PROFILE_IMAGE", linked_user=item.linked_user
            ).first()
            if uf:
                uf.unique_id = unique_id
                uf.save()
            else:
                uf = UserFile(
                    key="PROFILE_IMAGE",
                    unique_id=unique_id,
                    linked_user=item.linked_user,
                    user=info.context.user,
                    organization=org,
                )
                uf.save()
        return UpdateSalonBeautician(ok=True, beautician=item)


class UpdateMyProfile(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=False)
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        phone = graphene.String(required=False)
        unique_id = graphene.String(required=False)

    ok = graphene.Boolean()
    beautician = graphene.Field(BeauticianType)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        org = user.get_organization()

        user.email = kwargs.get("email") or user.email
        user.first_name = kwargs.get("first_name") or user.first_name
        user.last_name = kwargs.get("last_name") or user.last_name

        beautician = user.linked_user_id.filter(organization=org).first()
        beautician.phone = kwargs.get("phone") or beautician.phone
        beautician.address = kwargs.get("address") or beautician.address

        user.save(update_fields=["email", "first_name", "last_name"])
        beautician.save(update_fields=["phone", "address"])

        unique_id = kwargs.get("unique_id", "")
        if unique_id != "":
            uf = UserFile.objects.filter(key="PROFILE_IMAGE", linked_user=user).first()
            if uf:
                uf.unique_id = unique_id
                uf.save(update_fields=["unique_id"])
            else:
                uf = UserFile(
                    key="PROFILE_IMAGE",
                    unique_id=unique_id,
                    linked_user=user,
                    user=user,
                    organization=org,
                )
                uf.save()
        return UpdateSalonBeautician(ok=True, beautician=beautician)


class Mutation(graphene.ObjectType):
    salon_beautician_create = CreateSalonBeautician.Field()
    salon_beautician_update = UpdateSalonBeautician.Field()
    salon_beautician_delete = DeleteSalonBeautician.Field()
    edit_my_profile = UpdateMyProfile.Field()


schema_salon_beautician = graphene.Schema(query=Query, mutation=Mutation)
