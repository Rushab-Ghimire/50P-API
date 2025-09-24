from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class Service(BaseModelV2):
    title = models.CharField(null=False, default=None, max_length=255)
    code = models.CharField(null=False, default=None, max_length=255)
    sales_price = models.FloatField(default=0.0) #Normal Variant
    cost_price = models.FloatField(default=0.0) #Normal Variant
    category = models.ForeignKey(
        'salon.Category',
        on_delete = models.SET_NULL,
        null = True,
        related_name="services"
    )
    ttl_hrs = models.IntegerField(default=0)
    ttl_min = models.IntegerField(default=0)

    def generate_time_string(self):
        time_ = ""

        if self.ttl_hrs:
            time_ = f"{self.ttl_hrs} hr{'s' if self.ttl_hrs > 1 else ''} "

        if self.ttl_min:
            time_ += f"{self.ttl_min} min{'s' if self.ttl_min > 1 else 'min'}"

        return time_

    def __str__(self):
        return f"{self.title}"
