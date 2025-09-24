from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class Order(BaseModelV2):
    order_code = models.CharField(null=False, default=None, max_length=255)
    booking = models.ForeignKey(
        'salon.Booking',
        on_delete = models.SET_NULL,
        null = True
    )
    customer = models.ForeignKey(
        'salon.CustomerSalon',
        on_delete = models.SET_NULL,
        null = True,
        related_name="orders"
    )
    total = models.FloatField(default=0.0)
    receipt_number = models.CharField(null=False, default=None, max_length=255)

    def __str__(self):
        return f"{self.order_code}"
