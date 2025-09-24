import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from rest_framework import serializers

class ADMedia(BaseModelV2):
    class Meta:
        db_table = "ad_media"

    unique_id = models.CharField(null=False, max_length=36)
    file_path = models.ImageField(
        null=False, upload_to=os.path.join("upload", "ad", "media")
    )

    def __str__(self):
        return f"{self.file_path}"


class ADMediaSerializer(serializers.ModelSerializer):
    """Serializer for uploading media."""

    class Meta:
        model = ADMedia
        fields = ["id", "unique_id", "file_path"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "file_path": {"required": "True"},
            "unique_id": {"required": "True"},
        }
