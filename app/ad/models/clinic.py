from django.db import models
from core.base import BaseModelV2


class Clinic(BaseModelV2):

    class Meta:
        db_table = "ad_clinic"

    title = models.CharField(max_length=255)
    address=models.TextField(null=True, default=None)

    def __str__(self):
        return f"{self.title}"
