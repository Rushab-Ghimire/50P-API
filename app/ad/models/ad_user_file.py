from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from django.conf import settings


class ADUserFileKeys(models.TextChoices):
    PROFILE_IMAGE = "PROFILE_IMAGE"


class ADUserFileTypes(models.TextChoices):
    MEDIA = "media"
    DOCUMENT = "document"


class ADUserFile(BaseModelV2):
    class Meta:
        db_table = "ad_user_file"

    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ad_files",
    )
    key = models.CharField(null=True, default=None, max_length=255)
    unique_id = models.CharField(null=False, max_length=36)

    def __str__(self):
        return f"{self.unique_id}"
