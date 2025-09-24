from django.db import models
from core.base import BaseModelV2


class CustomerNote(BaseModelV2):
    customer = models.ForeignKey(
        "salon.CustomerSalon",
        null=True,
        default=None,
        related_name="notes",
        on_delete=models.SET_NULL,
    )
    note = models.CharField(null=False, max_length=255)

    def __str__(self):
        return f"{self.note}"
