import os, uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from rest_framework import serializers

from django.core.exceptions import ValidationError

class ADAccessCode(BaseModelV2):
    class Meta:
        db_table = "ad_access_code"

    primary_concern = models.TextField()
    hear_about = models.CharField(max_length=255, null=True, default=None)
    code = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.content}"
