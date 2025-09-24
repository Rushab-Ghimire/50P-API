from django.db import models
from django.utils.translation import gettext_lazy as _
from core.base import BaseModelV2
from core.utils.tf_utils import get_customer_file_URL, get_amount_with_currency_code
from salon.models.user_file import UserFileKeys, UserFileTypes

class CustomerSalon(BaseModelV2):
    first_name = models.CharField(null=False, default=None, max_length=255)
    last_name = models.CharField(null=True, default=None, max_length=255)
    email = models.CharField(null=True, default=None, max_length=255)
    phone = models.CharField(null=True, default=None, max_length=255)
    address = models.CharField(null=True, default=None, max_length=255)
    #profile_image_unique_id = models.CharField(null=True, max_length=36)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def profile_pic(self):
        return get_customer_file_URL(
                customer_id=self.id,
                key=UserFileKeys.PROFILE_IMAGE,
                type=UserFileTypes.MEDIA,
            )

