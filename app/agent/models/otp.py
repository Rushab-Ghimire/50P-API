from django.db import models
from core.base import BaseModelV2

class Otp(BaseModelV2):
    phone = models.CharField(max_length=16)
    unique_id = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.unique_id} - {self.number}"