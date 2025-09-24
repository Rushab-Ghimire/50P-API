from django.db import models
from core.base import BaseModel
from django.conf import settings


class Chargebee(BaseModel):
    class Meta:
        db_table = "payment_chargebee"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="chargebee",
    )

    customer_id = models.CharField(
        verbose_name="Customer Id from chargebee",
        null=True,
        max_length=36,
        default=None,
    )

    def __str__(self):
        return f"{self.id}"
