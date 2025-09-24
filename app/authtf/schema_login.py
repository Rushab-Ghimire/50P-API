import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import create_refresh_token, get_token

from authtf.models import SmsCode, SocialLogin, ProviderType, Role
from salon.models import Beautician
from organization.models import Organization
from authtf.schema_user import UserType
from core.utils.social_logins import get_google_user_info
from core.utils.tf_utils import send_sms, get_otp
from authtf.models import User
from graphql import GraphQLError
from django.apps import apps
from django.db import transaction
from django.contrib.auth import get_user_model
from ad.models import (ReferralCode, Referral)
from core.utils.tf_utils import (
    referralEmailChain,
)
from subscription.helpers import SubscriptionHelper


class LoginByPhone(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        sms_code = graphene.String(required=True)

    def mutate(self, info, sms_code):
        try:
            u = SmsCode.objects.get(sms_code=sms_code)
        except SmsCode.DoesNotExist:
            raise Exception("Invalid Code")
        token = get_token(u.linked_user)
        refresh_token = create_refresh_token(u.linked_user)
        u.delete()
        return LoginByPhone(
            user=u.linked_user, token=token, refresh_token=refresh_token
        )


class LoginByEmail(graphene.Mutation):
    # yo pachi google token based banaunuparcha
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        try:
            u = User.objects.get(email=email)
        except SmsCode.DoesNotExist:
            raise Exception("This Email is not registered in our System")
        token = get_token(u)
        refresh_token = create_refresh_token(u)
        return LoginByPhone(user=u, token=token, refresh_token=refresh_token)


class UserTypePhone(DjangoObjectType):
    class Meta:
        model = SmsCode
        fields = "__all__"


class UserDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(UserTypePhone)

    class Meta:
        fields = ["totalCount", "rows"]


class SendOtp(graphene.Mutation):
    sms_code = graphene.Field(UserDataModelType)

    class Arguments:
        phone = graphene.String(required=True)
        app = graphene.String()

    def mutate(self, info, phone, **kwargs):

        app = kwargs.get("app", "tfa")
        if app == "tfa":
            try:
                beautician = Beautician.objects.get(phone=phone)
            except Beautician.DoesNotExist:
                raise Exception("This phone number is not registered in our system")
            six_digit_code = get_otp()
            SmsCode.objects.filter(linked_user=beautician.linked_user).delete()
            s = SmsCode(linked_user=beautician.linked_user, sms_code=six_digit_code)
            s.save()

            send_sms(
                beautician.phone, f"Your TileFlexAI Login OTP Code is {six_digit_code}"
            )

        if app == "daysiai":
            try:
                beautician = get_user_model().objects.get(phone=phone)
            except Beautician.DoesNotExist:
                raise Exception("This phone number is not registered in our system")
            six_digit_code = get_otp()
            SmsCode.objects.filter(linked_user=beautician).delete()
            s = SmsCode(linked_user=beautician, sms_code=six_digit_code)
            s.save()

            send_sms(
                beautician.phone, f"Your DaysiAI Login OTP Code is {six_digit_code}"
            )

        return SendOtp(sms_code=s)


def _get_google_userinfo(token):
    response = get_google_user_info(token)
    data = response.json()
    if data.get("error"):
        raise GraphQLError("Please enter valid credentials")

    return {
        "email": data.get("email"),
        "first_name": data.get("given_name"),
        "last_name": data.get("family_name"),
        "provider_id": data.get("id"),
        "profile_image": data.get("picture"),
    }


class UserSocialLogin(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        provider = graphene.String(required=True)
        access_token = graphene.String(required=True)
        organization_id = graphene.Int()
        role_identifier = graphene.String()
        referral_code = graphene.String()

    def mutate(self, info, provider, access_token, organization_id=None, role_identifier=None, referral_code=None):
        if provider == ProviderType.GOOGLE:
            provider_data = _get_google_userinfo(access_token)
        else:
            raise GraphQLError("Invaild provider")

        try:
            user = User.objects.prefetch_related("social_logins").get(email=provider_data.get("email"))
        except User.DoesNotExist:
            user = None

        with transaction.atomic():
            create_social_login = False
            if user:
                if not user.social_logins.filter(provider=provider):
                    create_social_login = True
            else:
                user = User.objects.create_user(
                    email=provider_data.get("email"),
                    first_name=provider_data.get("first_name"),
                    last_name=provider_data.get("last_name"),
                    password=None,
                    is_active=True,
                )

                if organization_id is not None and role_identifier is not None:
                    # For AskDaysi
                    try:
                        organization = Organization.objects.get(id=organization_id)
                        if organization and organization.business and organization.business.id == 1:
                            role = Role.objects.get(identifier=role_identifier)

                            UserOrganization = apps.get_model("authtf", "UserOrganization")
                            user_organization, _ = UserOrganization.objects.get_or_create(
                                user=user, organization=organization
                            )
                            user_organization.role.add(role)

                    except Organization.DoesNotExist:
                        raise GraphQLError("Invalid organization ID.")
                    except Role.DoesNotExist:
                        raise GraphQLError("Invalid role identifier")

                else:
                    Beautician.objects.create(linked_user=user,user=user)

                try:
                    if referral_code is not None:
                        referral_code_obj = ReferralCode.objects.filter(code=referral_code).first()
                        if referral_code_obj is not None:
                            referral = Referral.objects.create(
                                    referred_user = user,
                                    referral_code = referral_code_obj,
                                    user = referral_code_obj.user
                                )
                            referralEmailChain(referral)
                        else:
                            try:
                                SubscriptionHelper.assign_default_subscription_for_new_user(user)
                            except Exception as e:
                                print(e)

                except Exception as e:
                    pass

                create_social_login = True

            if create_social_login:
                SocialLogin.objects.create(
                    user=user,
                    provider_id=provider_data.get("provider_id"),
                    provider=provider,
                    profile_image=provider_data.get("profile_image"),
                )


            token = get_token(user)
            refresh_token = create_refresh_token(user)

            return UserSocialLogin(user=user, token=token, refresh_token=refresh_token)


class Query(graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    login_by_phone = LoginByPhone.Field()
    login_by_email = LoginByEmail.Field()
    send_otp = SendOtp.Field()
    login_by_social = UserSocialLogin.Field()


schema_login = graphene.Schema(query=Query, mutation=Mutation)
