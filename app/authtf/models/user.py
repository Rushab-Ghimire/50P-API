"""
Database models.
"""

from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers
from authtf.models import Customer
from salon.models import Beautician
from core.utils.email_utils import EmailUtils
from core.utils import tf_utils
from authtf.models.user_organization import (
    OrganizationRoleSerializer,
    OrganizationRoleSettingSerializer,
)
from django.apps import apps
from salon.models import UserFile
from salon.models.user_file import UserFileTypes
from django.db.models import Q

from ad.models import ADUserFile
from ad.models.ad_user_file import ADUserFileTypes
from ad.models import ADAccessCode
from datetime import datetime, timezone
from ad.models import (ReferralCode, Referral)
from core.utils.tf_utils import (
    referralEmailChain,
)
from subscription.helpers import SubscriptionHelper


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email=None, password=None, **extra_fields):
        """Create, save and return a new user."""
        # if not email:
        #     raise ValueError("User must have an email address.")

        if email:
            user = self.model(email=self.normalize_email(email), **extra_fields)
        else:
            user = self.model(**extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, null=True, blank=True, unique=True, default=None)
    # name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    verification_code = models.CharField(max_length=36, null=True)
    password_reset_code = models.CharField(max_length=36, null=True)
    # organizations = models.ManyToManyField(Organization)
    organizations = models.ManyToManyField(
        "organization.Organization", through="authtf.UserOrganization"
    )
    phone = models.CharField(max_length=20, blank=True, default=None, null=True, unique=True)
    default_language = models.ForeignKey('ad.Language', on_delete=models.CASCADE, null=True, default=None, related_name="default_language")
    default_ethnicity = models.ForeignKey('ad.Ethnicity', on_delete=models.CASCADE, null=True, default=None, related_name="default_ethnicity")
    created_date = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def profile_pic(self):
        org = self.get_organization()
        b_id = org.business_id if org else None
        if b_id == 1 :
            uf = ADUserFile.objects.filter(key="PROFILE_IMAGE", linked_user=self).first()
        else:
            uf = UserFile.objects.filter(key="PROFILE_IMAGE", linked_user=self).first()

        if uf and uf.unique_id:
            if b_id == 1 :
                return tf_utils.get_ad_file_URL_by_unique_id(
                    uf.unique_id.lower(), ADUserFileTypes.MEDIA
                )
            else:
                return tf_utils.get_file_URL_by_unique_id(
                    uf.unique_id.lower(), UserFileTypes.MEDIA
                )

        social_login = (
            self.social_logins.exclude(profile_image__isnull=True)
            .exclude(profile_image="")
            .first()
        )
        if social_login:
            return social_login.profile_image

        if b_id == 1 :
            return tf_utils.get_ad_file_URL_by_unique_id(None, ADUserFileTypes.MEDIA)
        else:
            return tf_utils.get_file_URL_by_unique_id(None, UserFileTypes.MEDIA)

    def one_time_pass(self):
        _obj = ADAccessCode.objects.filter(user=self).filter(code="one-time-done").first()
        return False if _obj == None else True

    def business_id(self):
        return 1

    def get_organization(self):
        """
        Organization that is selected.
        Although user belongs to many organization, we will use first organization.
        [TO DO] User will select organization and maintain it through some field.
        """
        return self.organizations.first()

    def generate_verification_code(self):
        """Unique verification url for new registration"""
        self.verification_code = tf_utils.get_unique_key()
        self.save()

    def get_verification_url(self):
        org = self.get_organization()
        b_id = org.business_id if org else None
        APP_X_URL = settings.SYSTEM_APP_URL
        if b_id == 1 :
            APP_X_URL = "https://app.askdaysi.com"

        return f"{APP_X_URL}/confirm-email?code={self.verification_code}"

    def get_chargebee_customer(self):
        return self.chargebee.order_by("-created_date").first()

    def get_chargebee_customer_id(self):
        cb_obj = self.get_chargebee_customer()
        if cb_obj:
            return cb_obj.customer_id


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    organizations = OrganizationRoleSerializer(
        many=True, read_only=True, source="userorganization_set"
    )

    invitation_token = serializers.CharField(write_only=True, required=False)
    role_identifier = serializers.CharField(write_only=True, required=False)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    referral_code = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "organizations",
            "invitation_token",
            "profile_pic",
            "role_identifier",
            "organization_id",
            "phone",
            "referral_code",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "email": {"required": False},
            "phone": {"required": False},
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        with transaction.atomic():
            invitation_token = validated_data.pop("invitation_token", None)

            role_identifier = validated_data.pop("role_identifier", None)
            organization_id = validated_data.pop("organization_id", None)
            referral_code = validated_data.pop("referral_code", None)

            email = validated_data.get("email")
            phone = validated_data.get("phone")

            if not email and not phone:
                raise serializers.ValidationError("Email or phone is required.")

            if not phone or phone.strip() == "":
                validated_data["phone"] = f"{tf_utils.get_otp(10)}"

            organization = None
            if invitation_token:
                InvitationModel = apps.get_model("authtf", "Invitation")
                invitation_obj = InvitationModel.objects.filter(
                    unique_id=invitation_token
                ).first()
                if not invitation_obj:
                    raise serializers.ValidationError("Invalid token.")
                organization = invitation_obj.organization
                invitation_obj.delete()

            elif organization_id is not None:
                OrganizationModel = apps.get_model("organization", "Organization")
                organization = OrganizationModel.objects.filter(
                    id=organization_id
                ).first()
                if not organization:
                    raise serializers.ValidationError("Invalid organization ID.")

            user = get_user_model().objects.create_user(
                **validated_data, is_active=False
            )

            if organization:
                UserOrganization = apps.get_model("authtf", "UserOrganization")
                user_organization, _ = UserOrganization.objects.get_or_create(
                    user=user, organization=organization
                )
                Role = apps.get_model("authtf", "Role")

                if organization.business and organization.business.id == 1:
                    # For AskDaysi
                    try:
                        role = Role.objects.get(identifier=role_identifier)
                    except Role.DoesNotExist:
                        raise serializers.ValidationError("Invalid role identifier")
                else:
                    role = Role.objects.get(identifier="general")
                    beautician = Beautician.objects.create(linked_user=user, user=user)
                    beautician.organization.add(organization)

                user_organization.role.add(role)

            else:
                Beautician.objects.create(linked_user=user, user=user)

            if email and email.strip() != "":
                user.generate_verification_code()
                verification_url = user.get_verification_url()
                EmailUtils.registered_email_verification(user.email, verification_url, organization.business.id)

            else:
                generated_email = f"{user.first_name}{user.id}{tf_utils.get_otp(3)}@askdaysi.com"
                user.email = generated_email
                user.is_active = True
                user.save(update_fields=["email", "is_active"])

            Customer.objects.create(user=user)

            try:
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

        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError({"error": [msg]}, code="authorization")

        attrs["user"] = user
        return attrs


class VerifyNewUserSerializer(serializers.Serializer):
    verification_code = serializers.CharField()


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UpdatePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True, min_length=5)
    confirm_password = serializers.CharField(write_only=True, required=True)


class WhoAmISerializer(serializers.ModelSerializer):
    """Serializer for the user object for whoami endpoint."""

    organizations = OrganizationRoleSettingSerializer(
        many=True, read_only=True, source="userorganization_set"
    )

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "profile_pic",
            "organizations",
            "phone",
            "one_time_pass",
        ]
