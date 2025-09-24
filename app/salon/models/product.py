from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class Product(BaseModelV2):
    title = models.CharField(null=False, default=None, max_length=255)
    sales_price = models.FloatField(default=0.0) #Normal Variant
    cost_price = models.FloatField(default=0.0) #Normal Variant
    category = models.ForeignKey(
        'salon.Category',
        on_delete = models.SET_NULL,
        null = True
    )

    def __str__(self):
        return f"{self.title}"
