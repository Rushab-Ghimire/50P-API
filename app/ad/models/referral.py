import os, uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from rest_framework import serializers
from django.conf import settings

from django.core.exceptions import ValidationError

class Referral(BaseModelV2):
    class Meta:
        db_table = "ad_referral"

    referred_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="user_referral",
    )
    referral_code = models.ForeignKey('ReferralCode', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.referral_code.code}"
