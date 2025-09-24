import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import create_refresh_token, get_token
from graphene.types.json import JSONString
from authtf.models import Role, UserOrganization
from graphql import GraphQLError
from django.db.models import Q


from authtf.models.user import UserSerializer, WhoAmISerializer
from salon.models import Beautician
from ad.schemas.doctor import DoctorType

class UserType(DjangoObjectType):
    role = graphene.String()
    doctor = graphene.Field(DoctorType)
    profile_pic = graphene.String()
    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'phone', 'role', 'doctor', 'profile_pic']

    def resolve_role(self, info):
        user_organization = self.userorganization_set.first()
        if user_organization and user_organization.role.exists():
            return user_organization.role.first().name
        return None

    def resolve_doctor(self, info):
        if self.doctor_set.exists():
            return self.doctor_set.first()
        return None

    def resolve_profile_pic(self, info):
        return self.profile_pic()


class UserDetailType(DjangoObjectType):
    profile_pic = graphene.String()
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
        ]
    def resolve_profile_pic(self, info):
        return self.profile_pic()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()
    class Arguments:
        password = graphene.String(required=True)
        email = graphene.String(required=True)
    def mutate(self, info, password, email):
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        Beautician.objects.create(linked_user=user, user=user)

        token = get_token(user)
        refresh_token = create_refresh_token(user)
        return CreateUser(user=user, token=token, refresh_token=refresh_token)


class UpdateRole(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        role_identifier = graphene.String(required=True)

    @login_required
    def mutate(self, info, role_identifier):
        user = info.context.user
        organization = user.get_organization()

        if not (organization and organization.business.id == 1):
            raise GraphQLError("Invalid action")

        try:
            role = Role.objects.get(identifier=role_identifier)
            user_organization, _ = UserOrganization.objects.get_or_create(
                user=user, organization=organization
            )
            user_organization.role.clear()
            user_organization.role.add(role)
        except Role.DoesNotExist:
            raise GraphQLError("Invalid role identifier")

        return UpdateRole(ok=True)


class UserDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(UserType)

    class Meta:
        fields = ("totalCount", "rows")

class Query(graphene.ObjectType):

    user = graphene.Field(
        UserDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    whoami = graphene.Field(JSONString)

    def resolve_user(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            filter = Q(first_name__icontains=search)

        qs = get_user_model().objects.filter(filter)
        qs = qs.order_by("-created_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return UserDataModelType(totalCount=totalCount, rows=qs)

    def resolve_whoami(self, info):
        user = info.context.user
        # Check if user is authenticated
        if user.is_anonymous:
            raise Exception("Authentication Failure: Your must be signed in")

        # serializer = UserSerializer(user)
        serializer = WhoAmISerializer(user)
        return serializer.data

    # Check if user is authenticated using decorator
    @login_required
    def resolve_users(self, info):
        return get_user_model().objects.all()

class TokenAuth(graphene.Mutation):
    token = graphene.String()
    refresh_token = graphene.String()
    payload = graphene.Field(JSONString)
    refreshExpiresIn = graphene.Int()

    class Arguments:
        email = graphene.String()
        phone = graphene.String()
        password = graphene.String(required=True)

    def mutate(seld, info, **kwargs):

        email = kwargs.get('email')
        phone = kwargs.get('phone')
        password= kwargs.get('password')

        if not email and not phone:
            raise GraphQLError("Email or phone is required")

        if email:
            user = get_user_model().objects.filter(email=email).first()
        elif phone:
            user = get_user_model().objects.filter(phone=phone).first()

        if not user or not user.check_password(password):
            raise GraphQLError("Invalid credentials")

        return TokenAuth(token=get_token(user), refresh_token=create_refresh_token(user))


class Mutation(graphene.ObjectType):
    # token_auth_ref = graphql_jwt.ObtainJSONWebToken.Field()
    token_auth = TokenAuth.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    verify_token = graphql_jwt.Verify.Field()
    create_user = CreateUser.Field()
    udpate_role = UpdateRole.Field()

schema_user = graphene.Schema(query=Query, mutation=Mutation)
