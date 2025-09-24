from django.db import models
from core.base import BaseModelV2
from rest_framework import serializers
from core.utils import tf_utils
from salon.models.user_file import UserFileTypes

class SettingKeys(models.TextChoices):
    LOGO = "logo"
    BUSINESS_PHONE = "business_phone"
    PUBLIC_URL = "public_url"

class Setting(BaseModelV2):
    key = models.CharField(null=False, max_length=255)
    value = models.CharField(null=False, max_length=255)

    def __str__(self):
        return f"{self.key} {self.value}"


def get_setting_by_key(key, org=None):
    if isinstance(key, str):
        key = [key]
    elif not isinstance(key, list):
        return Setting.objects.none()

    q = Setting.objects.filter(key__in=key)

    if org:
        q = q.filter(models.Q(organization=org))

    return q


def get_tax_settings(org_id):
    tax_maps = {"tax_1": "SGST Tax", "tax_2": "CGST Tax"}

    settings = (
        Setting.objects.filter(key__in=tax_maps.keys())
        .filter(organization_id=org_id)
        .values_list("key", "value")
    )
    taxes = [{"key": tax_maps[key], "value": value} for key, value in settings]
    return taxes


class SettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Setting
        fields = ["id", "key", "value"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.key == "logo":
            data["value"] = tf_utils.get_file_URL_by_unique_id(
                instance.value.lower(), UserFileTypes.MEDIA
            )
        return data
