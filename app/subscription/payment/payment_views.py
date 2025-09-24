from django.http import JsonResponse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from subscription.payment_serializer import (
    ChargebeeCreateSubscriptionSerializer,
    ChargebeeCustomerUpdateSerializer,
)

from core.authentication import GraphQLJWTAuthentication
from subscription.payment_utils import PaymentUtils
from django.core.exceptions import ValidationError
from rest_framework.decorators import action


class ChargebeeCreateSubscriptionView(generics.CreateAPIView, generics.UpdateAPIView):
    serializer_class = ChargebeeCreateSubscriptionSerializer
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        user = request.user
        chargebee_customer_id = user.get_chargebee_customer_id()
        if not chargebee_customer_id:
            customer = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        else:
            customer = {"id": chargebee_customer_id}

        customer["cf_ad_user_id"] = user.id

        planId = request.data.get("planId")

        try:

            response = PaymentUtils().get_chargebee_hosted_page_for_new_subscription(
                customer, planId
            )

        except Exception as ex:
            print(ex)
            return Response(
                {
                    "message": _(
                        "Unable to process the request. Please try again later."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return JsonResponse(response.hosted_page.raw_data, safe=False)

    def update(self, request):
        user = request.user
        chargebee_customer_id = user.get_chargebee_customer_id()
        if not chargebee_customer_id:
            return Response(
                {"error": "Unable to complete the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer = {"id": chargebee_customer_id}

        plan_id = request.data.get("planId")

        subscription_id = request.data.get("subscriptionId")

        if not subscription_id:
            return Response(
                {"error": "Unable to complete the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response = PaymentUtils().get_chargebee_hosted_page_for_update_subscription(
                subscription_id, plan_id, customer
            )

        except Exception as ex:
            print(ex)
            return Response(
                {
                    "message": _(
                        "Unable to process the request. Please try again later."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return JsonResponse(response.hosted_page.raw_data, safe=False)
        # return Response({"message": "Customer updated successfully"})

class ChargebeeCustomerView(generics.UpdateAPIView):
    serializer_class = ChargebeeCustomerUpdateSerializer
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        payment_utils = PaymentUtils()
        chargebee_customer_id = request.user.get_chargebee_customer_id()
        if not chargebee_customer_id:
            return Response(
                {"error": "Payment Customer not found for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_data = {}
        auto_collection = request.data.get("auto_collection", None)
        if auto_collection is not None:
            user_data["auto_collection"] = "on" if bool(auto_collection) else "off"

        if user_data != {}:
            payment_utils.update_customer(chargebee_customer_id, params=user_data)

        return Response({"message": "Customer updated successfully"})


class ChargebeeInvoiceView(viewsets.ViewSet):
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(
        methods=["GET"],
        detail=False,
        url_path="customer-invoices",
    )
    def customer_invoices(self, request):
        user = request.user
        invoices = PaymentUtils().get_invoices_for_user(
            user
        )

        return Response(invoices)


class ChargebeePaymentSourceView(viewsets.ViewSet):
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(
        methods=["POST"],
        detail=False,
        url_path="manage-payment-source",
    )
    def manage_payment_source(self, request):
        user = request.user
        chargebee_customer_id = user.get_chargebee_customer_id()
        if not chargebee_customer_id:
            return Response(
                {"error": "Payment Customer not found for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hosted_page = PaymentUtils().get_chargebee_hosted_page_to_manage_payment_sources(
            chargebee_customer_id
        )

        return Response(hosted_page)

    @action(
        methods=["GET"],
        detail=False,
        url_path="get-all-customer-cards",
    )
    def get_all_customer_cards(self, request):
        user = request.user
        chargebee_customer_id = user.get_chargebee_customer_id()
        if not chargebee_customer_id:
            return Response(
                {"error": "Payment Customer not found for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        res = PaymentUtils().get_all_cards_for_customer(
            chargebee_customer_id
        )

        return Response(res)


