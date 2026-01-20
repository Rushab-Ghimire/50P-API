from core.base import BaseModelV2
from django.db import models

class SMSLog(BaseModelV2):
    phone_number = models.CharField(max_length=15)
    message = models.CharField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.Charfield(max_length = 20, default = "Success")

    def __str__(self):
        return f"To: {self.phone_number} at {self.sent_at}"