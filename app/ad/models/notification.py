from django.db import models
from core.base import BaseModelV2
from django.conf import settings


class Notification(BaseModelV2):
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notifications",
    )
    content = models.TextField()
    data_x = models.TextField(default=None, null=True, blank=True)
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"
