from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class MembershipType(BaseModelV2):
    title = models.CharField(null=False, default=None, max_length=255)
    fee = models.FloatField(default=0.0)
    billing_period = models.IntegerField(default=1) #monthly, yearly

    def __str__(self):
        return f"{self.subscription_start_date}"
