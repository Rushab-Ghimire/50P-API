from django.db import models
from core.base import BaseModelV2

class Ehr(BaseModelV2):
    full_name = models.CharField(null=False, max_length=255)
    phone_number = models.CharField(null=False, max_length=255, default=None)
    booking_date_time = models.TextField(null=True, default=None)
    json = models.TextField(null=True, default=None)

    def __str__(self):
        return f"{self.full_name}"