from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response
from subscription.models import Chargebee, ChargebeeSubscription
from subscription.payment_utils import PaymentUtils


class ChargebeeWebhookEventTypes:
    CUSTOMER_CREATED = "customer_created"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_CHANGED = "subscription_changed"
    SUBSCRIPTION_DELETED = "subscription_deleted"
    SUBSCRIPTION_CANCELLATION_SCHEDULED = "subscription_cancellation_scheduled"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"


class ChargebeeWebhookHandler:
    def __init__(self, webhook_obj):
        self.webhook_obj = webhook_obj

    def get_or_create_chargebee_user(self):
        customer = self.webhook_obj["content"].get("customer", {})
        customer_id = customer.get("id")
        chargebee_user = Chargebee.objects.filter(customer_id=customer_id).first()

        if not chargebee_user:
            user_id = self.customer.get("cf_ad_user_id")
            if not user_id:
                return None, "User ID not provided"

            user = get_user_model().objects.filter(pk=user_id).first()
            if not user:
                return None, "User not found"

            chargebee_user, _ = Chargebee.objects.get_or_create(
                user=user,
                customer_id=customer_id,
            )

        return chargebee_user, None

    def customer_created(self):
        customer = self.webhook_obj["content"]["customer"]

        user = None
        if cf_ad_user_id := customer.get("cf_ad_user_id"):
            user = get_user_model().objects.filter(pk=cf_ad_user_id).first()

        elif email := customer.get("email"):
            user = get_user_model().objects.filter(email=email).first()

        if user is not None:
            Chargebee.objects.update_or_create(
                user=user,
                defaults={
                    "customer_id": customer.get("id"),
                },
            )

        return Response({"message": "Success"})

    def subscription_created(self):
        subscription = self.webhook_obj["content"]["subscription"]
        customer = self.webhook_obj["content"]["customer"]
        customer_id = customer.get("id")

        chargebee_user = Chargebee.objects.filter(customer_id=customer_id).first()

        if not chargebee_user:
            user_id = customer.get("cf_ad_user_id")
            if not user_id:
                return Response({"message": "User ID not provided"})

            user = get_user_model().objects.filter(pk=user_id).first()
            if not user:
                return Response({"message": "User not found"})

            chargebee_user, _ = Chargebee.objects.get_or_create(
                user=user,
                customer_id=customer_id,
            )

        ChargebeeSubscription.objects.update_or_create(
            chargebee=chargebee_user,
            subscription_id=subscription["id"],
            defaults={
                "metadata": subscription,
            },
        )

        return Response({"message": "Success"})

    def subscription_changed(self):
        subscription = self.webhook_obj["content"]["subscription"]
        customer = self.webhook_obj["content"]["customer"]
        customer_id = customer.get("id")

        chargebee_user = Chargebee.objects.filter(customer_id=customer_id).first()

        if not chargebee_user:
            user_id = customer.get("cf_ad_user_id")
            if not user_id:
                return Response({"message": "User ID not provided"})

            user = get_user_model().objects.filter(pk=user_id).first()
            if not user:
                return Response({"message": "User not found"})

            chargebee_user, _ = Chargebee.objects.get_or_create(
                user=user,
                customer_id=customer_id,
            )

        ChargebeeSubscription.objects.update_or_create(
            chargebee=chargebee_user,
            subscription_id=subscription["id"],
            defaults={
                "metadata": subscription,
            },
        )

        return Response({"message": "Success"})

    def subscription_cancelled(self):
        subscription = self.webhook_obj["content"]["subscription"]

        chargebee_user, error = self.get_or_create_chargebee_user()
        if error:
            return Response({"message": error})

        ChargebeeSubscription.objects.update_or_create(
            chargebee=chargebee_user,
            subscription_id=subscription["id"],
            defaults={
                "metadata": subscription,
            },
        )

        PaymentUtils().update_subscription(subscription_id=subscription["id"], params={
            "subscription_items": [
                {
                    "item_price_id": "Free-plan-USD-Monthly"
                }
            ]
        })

        return Response({"message": "Success"})

    def subscription_deleted(self):
        subscription = self.webhook_obj["content"]["subscription"]
        ChargebeeSubscription.objects.filter(
            subscription_id=subscription.get("id")
        ).delete()

        return Response({"message": "Success"})


class ChargebeeWebhookView(generics.CreateAPIView):

    def post(self, request):
        webhook_obj = request.data
        handler = ChargebeeWebhookHandler(webhook_obj)
        event_type = webhook_obj.get("event_type")

        if event_type == ChargebeeWebhookEventTypes.CUSTOMER_CREATED:
            return handler.customer_created()

        if event_type == ChargebeeWebhookEventTypes.SUBSCRIPTION_CREATED:
            return handler.subscription_created()

        if event_type in [
            ChargebeeWebhookEventTypes.SUBSCRIPTION_CHANGED,
            ChargebeeWebhookEventTypes.SUBSCRIPTION_CANCELLATION_SCHEDULED,
        ]:
            return handler.subscription_changed()

        if event_type == ChargebeeWebhookEventTypes.SUBSCRIPTION_CANCELLED:
            return handler.subscription_cancelled()

        if event_type == ChargebeeWebhookEventTypes.SUBSCRIPTION_DELETED:
            return handler.subscription_deleted()

        return Response({"message": "Success"})
