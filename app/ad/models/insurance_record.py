from django.db import models
from core.base import BaseModelV2

class InsuranceRecord(BaseModelV2):
    insurance_provider = models.ForeignKey('InsuranceProvider', on_delete=models.CASCADE)
    member_id = models.CharField(max_length=255)
    subscription_number = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.member_id} - {self.subscription_number}"