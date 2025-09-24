from django.db import models
from core.base import BaseModelV2


class Lab(BaseModelV2):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, default=None)
    address = models.TextField(null=True, default=None)
    country = models.ForeignKey("ad.Country", related_name="labs", null=True, default=None, on_delete=models.SET_NULL)
    city = models.ForeignKey("ad.City", related_name="labs", null=True, default=None, on_delete=models.SET_NULL)
    state = models.ForeignKey("ad.State", related_name="labs", null=True, default=None, on_delete=models.SET_NULL)
    lattitude = models.FloatField(null=True, default=None)
    longitude = models.FloatField(null=True, default=None)
    logo_uuid = models.CharField(null=True, default=None, max_length=36)
    insurance_providers = models.ManyToManyField("ad.InsuranceProvider", related_name="labs")

    def __str__(self):
        return f"{self.title}"
