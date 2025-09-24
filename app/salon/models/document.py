import os, uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from rest_framework import serializers

from django.core.exceptions import ValidationError

def validateDocument(file):
    valid_extensions = ['pdf', 'doc', 'docx', 'txt']
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in valid_extensions:
        raise ValidationError("Unsupported file extension. Allowed extensions are: pdf, doc, docx, txt.")

class Document(BaseModelV2):
    unique_id = models.CharField(null=False, max_length=36)
    file_path = models.FileField(
        null=False, upload_to=os.path.join("upload", "salon", "document"),
        validators=[validateDocument]
    )

    def __str__(self):
        return f"{self.title}"


class SalonDocumentSerializer(serializers.ModelSerializer):
    """Serializer for uploading media."""

    class Meta:
        model = Document
        fields = ["id", "unique_id", "file_path"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "file_path": {"required": "True"},
            "unique_id": {"required": "True"},
        }