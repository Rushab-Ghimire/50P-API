from django.db import models
from core.base import BaseModel
from django.conf import settings


class ChargebeeSubscription(BaseModel):
    class Meta:
        db_table = "payment_chargebee_subscription"

    chargebee = models.ForeignKey(
        "subscription.Chargebee",
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="subscriptions",
    )

    subscription_id = models.CharField(
        verbose_name="Subscription Id from chargebee",
        null=True,
        max_length=36,
        default=None,
    )

    metadata = models.JSONField(
        verbose_name="Subscription related data from Chargebee", null=True, default=None
    )

    def __str__(self):
        return f"{self.id}"
