"""
Views for the user API.
"""

from core.utils import tf_utils

from rest_framework import generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from core.authentication import GraphQLJWTAuthentication

from core.utils.email_utils import EmailUtils
from authtf.models.user import (
    UserSerializer,
    AuthTokenSerializer,
    VerifyNewUserSerializer,
    ResetPasswordRequestSerializer,
    UpdatePasswordSerializer,
)

from authtf.models import (
    User,
    Invitation
)
from django.apps import apps


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class VerifyNewUserView(APIView):
    serializer_class = VerifyNewUserSerializer

    def post(self, request):
        verification_code = request.data.get("verification_code")
        try:
            user = User.objects.get(verification_code=verification_code)
            user.is_active = True
            user.verification_code = None
            user.save()
            return Response(
                {"message": "Account verified successfully! Login to continue."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordRequestView(APIView):
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        """Request new passoword for a given email"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = None
        try:
            organization_id = request.data.get("organization_id", None)
            if organization_id is not None:
                OrganizationModel = apps.get_model("organization", "Organization")
                organization = OrganizationModel.objects.filter(
                    id=organization_id
                ).first()
                if not organization:
                    return Response(
                        {"error": "Invalid Organization."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            email = request.data.get("email")
            user = User.objects.get(email=email)
            full_name = f"{user.first_name} {user.last_name}"
            token = tf_utils.get_unique_key()
            b_id = organization.business_id if organization else None
            reset_url = tf_utils.get_password_reset_request_url(token, b_id)

            user.password_reset_code = token
            user.save()

            EmailUtils.password_reset_email(email, full_name, reset_url, organization.business.id)

        except User.DoesNotExist:
            return Response(
                {"error": "This email does not exist in our System."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "We have sent you an email with the link to reset your password"},
            status=status.HTTP_200_OK,
        )


class VerifyResetPasswordRequestView(APIView):
    def get(self, request, token):
        """Verify token for the request of password reset"""
        try:
            user = User.objects.get(password_reset_code=token)
            return Response(
                {"user": UserSerializer(user).data},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Invalid password reset token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordView(APIView):
    serializer_class = UpdatePasswordSerializer

    def post(self, request, token):
        """Update password of a user with given token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(password_reset_code=token)

        except User.DoesNotExist:
            return Response(
                {"error": "Invalid password reset token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return Response(
                {"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            user.set_password(password)
            user.password_reset_code = None
            user.save()

            return Response(
                {"message": "Password updated"},
                status=status.HTTP_200_OK,
            )

class SetInvitedUserPasswordView(APIView):
    serializer_class = UpdatePasswordSerializer

    def post(self, request, token):
        """Update password of a invited user with given token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            invitation = Invitation.objects.get(unique_id=token)
            user = invitation.linked_user
            if not user:
                raise User.DoesNotExist()

        except (Invitation.DoesNotExist, User.DoesNotExist):
            return Response(
                {"error": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return Response(
                {"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            user.set_password(password)
            user.save(update_fields=["password"])
            invitation.delete()

            return Response(
                {"message": "Password updated"},
                status=status.HTTP_200_OK,
            )
