import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from authtf.models import Invitation, User
from django.conf import settings
from core.utils.tf_utils import get_unique_key
from core.utils.email_utils import EmailUtils
from sendgrid.helpers.mail import Content
from graphql_jwt.decorators import login_required
from graphql import GraphQLError


class InvitationType(DjangoObjectType):
    class Meta:
        model = Invitation
        fields = "__all__"


class InvitationDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(InvitationType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    invitation = graphene.Field(
        InvitationDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    invitation_by_id = graphene.Field(InvitationType, id=graphene.Int())
    invitation_by_unique_id = graphene.Field(
        InvitationType, unique_id=graphene.String()
    )

    @login_required
    def resolve_invitation(self, info, **kwargs):
        org = info.context.user.get_organization()

        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        qs = Invitation.objects.filter(organization=org)
        qs = qs.filter(is_deleted = False)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return InvitationDataModelType(totalCount=totalCount, rows=qs)

    def resolve_invitation_by_id(root, info, id):
        return Invitation.objects.get(pk=id)

    def resolve_invitation_by_unique_id(root, info, unique_id):
        return Invitation.objects.get(unique_id=unique_id)


class CreateInvitation(graphene.Mutation):
    class Arguments:
        to_user = graphene.Int(required=False)
        email = graphene.String(required=False)

    ok = graphene.Boolean()
    invitation = graphene.Field(InvitationType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        if not org:
            raise GraphQLError("You do not belong to any organization.")

        to_user_id = kwargs.get("to_user", None)
        email = kwargs.get("email", None)

        if not email and not to_user_id:
            raise Exception("Provide user_id or email")

        _user = None
        existing_invitation = None
        if to_user_id != None:
            _user = User.objects.get(pk=to_user_id)

            try:
                existing_invitation = Invitation.objects.get(
                    linked_user=_user, organization=org
                )
            except Invitation.DoesNotExist:
                pass

        unique_id = get_unique_key()
        item = None
        if existing_invitation != None:
            existing_invitation.unique_id = unique_id
            existing_invitation.save()
            item = existing_invitation
        else:
            if _user:
                item = Invitation(
                    linked_user=_user,
                    organization=org,
                    unique_id=unique_id,
                    user=session_user,
                )
            else:
                item = Invitation(
                    organization=org, unique_id=unique_id,
                    user=session_user, email = email
                )
            item.save()

        if _user:
            invitation_link = f"{settings.SYSTEM_APP_URL}/invite-user?code={unique_id}"
            to_email = _user.email
            to_name = f"{_user.first_name} {_user.last_name}"
            name = _user.first_name
        else:
            invitation_link = f"{settings.SYSTEM_APP_URL}/invite?code={unique_id}"
            to_email = email
            to_name = ""
            name = ""

        EmailUtils.invitation_email(to_email=to_email, to_name=to_name, name=name, organization=org.name, invtation_url=invitation_link)

        return CreateInvitation(ok=True, invitation=item)

class DeleteInvitation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    def mutate(self, info, id):
        item = Invitation.objects.get(pk=id)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteInvitation(ok=True)

class Mutation(graphene.ObjectType):
    invitation_create = CreateInvitation.Field()
    invitation_delete = DeleteInvitation.Field()


schema_invitation = graphene.Schema(query=Query, mutation=Mutation)
