from django.db import models
from core.base import BaseModelV2
from django.utils.text import slugify


class Doctor(BaseModelV2):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    specialization = models.ManyToManyField("ad.Specialization", related_name="doctors")
    description = models.TextField(null=True, default=None)
    address = models.CharField(max_length=255, null=True, default=None)
    city = models.ForeignKey(
        "ad.City", on_delete=models.SET_NULL, null=True, default=None
    )
    state = models.ForeignKey(
        "ad.State", on_delete=models.SET_NULL, null=True, default=None
    )
    country = models.ForeignKey(
        "ad.Country", on_delete=models.SET_NULL, null=True, default=None
    )
    postal_code = models.CharField(max_length=16, null=True, default=None)
    website = models.URLField(null=True, default=None)
    phone = models.CharField(max_length=20, null=True, default=None)
    phone_official = models.CharField(max_length=20, null=True, default=None)
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    timezone = models.CharField(max_length=64, null=True, default=None)
    is_premium = models.BooleanField(default=False)
    appointment_cost = models.FloatField(null=True, default=None)
    source = models.CharField(max_length=10, null=True, default=None)

    def generate_slug(text):
        original_slug = slug = slugify(text)
        counter = 1
        while Doctor.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def __str__(self):
        return f"{self.name}"
