from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class OrderDetail(BaseModelV2):
    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    subtotal = models.FloatField(default=0.0)
    entity_id = models.IntegerField(default=0)
    entity_type = models.ForeignKey(
        'salon.EntityType',
        on_delete = models.SET_NULL,
        null = True
    )
    order = models.ForeignKey(
        'salon.Order',
        on_delete = models.SET_NULL,
        null = True,
        related_name="order_details"
    )

    def __str__(self):
        return f"{self.order.order_code}"
