from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2

class SessionStatus(BaseModelV2):
    title = models.CharField(null=False, default=None, max_length=255)

    def __str__(self):
        return f"{self.title}"
