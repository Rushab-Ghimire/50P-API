from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class PaymentMethodSet(models.IntegerChoices):
    CASH = 1, "Cash"
    BANK = 2, "Bank"
    NONE = 0, "None"

class Payment(BaseModelV2):
    payment_method = models.IntegerField(null=False, default=0) #1=Cash, 2=Bank
    amount = models.FloatField(default=0.0)
    order = models.ForeignKey(
        'salon.Order',
        on_delete = models.SET_NULL,
        null = True,
        related_name="payments"
    )

    def __str__(self):
        return f"{self.order.order_code}"
