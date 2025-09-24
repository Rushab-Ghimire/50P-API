from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from django.conf import settings


class UserFileKeys(models.TextChoices):
    PROFILE_IMAGE = "PROFILE_IMAGE"


class UserFileTypes(models.TextChoices):
    MEDIA = "media"
    DOCUMENT = "document"


class UserFile(BaseModelV2):
    class Meta:
        db_table = "salon_user_file"

    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="files",
    )
    key = models.CharField(null=True, default=None, max_length=255)
    unique_id = models.CharField(null=False, max_length=36)
    customer = models.ForeignKey(
        "salon.CustomerSalon",
        on_delete=models.SET_NULL,
        null=True,
        related_name="files",
    )

    def __str__(self):
        return f"{self.unique_id}"
