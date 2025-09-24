import os, uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from rest_framework import serializers

from django.core.exceptions import ValidationError

class ReferralCode(BaseModelV2):
    class Meta:
        db_table = "ad_referral_code"

    code = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.code}"
