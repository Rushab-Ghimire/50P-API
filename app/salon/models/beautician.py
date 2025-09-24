from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from django.conf import settings

class Beautician(BaseModelV2):
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
        related_name='linked_user_id'
    )
    phone = models.CharField(null=True, default=None, max_length=255)
    address = models.TextField(null=True, default=None)

    def __str__(self):
        return f"{self.linked_user.first_name} {self.linked_user.last_name}"
