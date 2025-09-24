from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class MembershipService(BaseModelV2):
    membership_type = models.ForeignKey(
        "salon.MembershipType",
        on_delete = models.SET_NULL,
        null = True
    )
    service = models.ForeignKey(
        "salon.Service",
        on_delete = models.SET_NULL,
        null = True
    )
    variant = models.ForeignKey(
        "salon.Variant",
        on_delete = models.SET_NULL,
        null = True
    )

    def __str__(self):
        return f"{self.membership_type}"
