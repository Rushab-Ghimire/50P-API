from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from django.conf import settings

class SmsCode(BaseModelV2):
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
        related_name='sms_codes'
    )
    sms_code = models.CharField(null=False, default=None, max_length=10)

    def __str__(self):
        return f"{self.sms_code}"
