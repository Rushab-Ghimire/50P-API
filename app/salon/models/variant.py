from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class Variant(BaseModelV2):
    title = models.CharField(null=False, default=None, max_length=255)
    sales_price = models.FloatField(default=0.0)
    cost_price = models.FloatField(default=0.0)
    entity_type = models.ForeignKey(
        'salon.EntityType',
        on_delete = models.SET_NULL,
        null = True
    )
    entity_id = models.IntegerField(default=None) #depends on entity_type

    def __str__(self):
        return f"{self.title}"
