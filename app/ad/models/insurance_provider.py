from django.db import models
from core.base import BaseModelV2


class InsuranceProvider(BaseModelV2):

    class Meta:
        db_table = "ad_insurance_provider"

    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255, null=True, default=None)
    location = models.CharField(max_length=255, null=True, default=None)
    doctor = models.ManyToManyField("ad.Doctor", related_name="insurance_providers")

    def __str__(self):
        return f"{self.name}"
