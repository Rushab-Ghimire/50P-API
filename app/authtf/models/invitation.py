from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from django.conf import settings

class Invitation(BaseModelV2):
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
        related_name='invitations'
    )
    unique_id = models.CharField(null=True, max_length=36)
    email = models.EmailField(max_length=255, null=True)

    def __str__(self):
        return f"{self.unique_id}"
