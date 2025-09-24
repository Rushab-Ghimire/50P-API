from rest_framework import permissions, viewsets, status
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response


from core.authentication import GraphQLJWTAuthentication
from subscription.payment_utils import PaymentUtils
from subscription.utils import *
from subscription.subscription_serializer import CancelSubscriptionSerializer, UpdateSubscriptionSerializer


class SubscriptionView(viewsets.ViewSet):
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CancelSubscriptionSerializer

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'update_subscription':
            return UpdateSubscriptionSerializer

        return self.serializer_class

    @action(
        methods=["GET"],
        detail=False,
        url_path="current-subscription",
    )
    def current_subscription(self, request):
        try:
            payment_util = PaymentUtils()
            subscription = payment_util.get_current_subscription_for_user(request.user)
            if subscription:
                return Response(subscription)
        except Exception as e:
            print(e)
            return Response(
                {"error": "Unable to process"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({})

    @action(
        methods=["PUT"],
        detail=False,
        url_path="update-current-subscription",
    )
    def update_current_subscription(self, request):
        payment_utils = PaymentUtils()
        chargebee_customer = request.user.get_chargebee_customer()
        if not chargebee_customer:
            return Response(
                {"error": "Payment Customer not found for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = chargebee_customer.subscriptions.first()
        if not subscription:
            return Response(
                {"error": "Subscription not found for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription_data = {}
        auto_collection = request.data.get("auto_collection", None)
        if auto_collection is not None:
            subscription_data["auto_collection"] = "on" if bool(auto_collection) else "off"

        if subscription_data != {}:
            payment_utils.update_subscription(subscription.subscription_id, params=subscription_data)

        return Response({"message": "Subscription updated successfully"})


    @action(
        methods=["POST"],
        detail=False,
        url_path="cancel-current-subscription",
    )
    def cancel_current_subscription(self, request):

        user = request.user
        chargebee_customer = user.chargebee.order_by("-created_date").first()

        if not chargebee_customer:
            return Response(
                {"error": _("Chargebee customer not found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription_id = request.data.get("subscriptionId")
        if not subscription_id:
            return Response(
                {"error": _("Subscription ID is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = chargebee_customer.subscriptions.filter(
            subscription_id=subscription_id
        ).first()

        if not subscription:
            return Response(
                {"error": _("Subscription not found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            PaymentUtils().cancel_subscription(
                subscription_id, {"cancel_option": "end_of_term"}
            )
            return Response(
                {"message": _("Subscription canceled successfully.")},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": _("Unable to process the request.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["POST"],
        detail=False,
        url_path="remove-current-subscription-scheduled-cancellation",
    )
    def remove_current_subscription_scheduled_cancellation(self, request):

        user = request.user
        chargebee_customer = user.chargebee.order_by("-created_date").first()

        if not chargebee_customer:
            return Response(
                {"error": _("Chargebee customer not found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription_id = request.data.get("subscriptionId")
        if not subscription_id:
            return Response(
                {"error": _("Subscription ID is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = chargebee_customer.subscriptions.filter(
            subscription_id=subscription_id
        ).first()

        if not subscription:
            return Response(
                {"error": _("Subscription not found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            PaymentUtils().remove_scheduled_cancellation(
                subscription_id
            )
            return Response(
                {"message": _("Subscription canceled successfully.")},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": _("Unable to process the request.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
