from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json
from django.forms.models import model_to_dict
from rest_framework import serializers
from core.base import BaseModel
from .package import Package

class Module(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
    )
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.CharField(blank=True, max_length=255)
    icon = models.CharField(blank=True, max_length=255)
    route = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.title} - {self.slug}"

class Quicklink(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    # add this to User model
    # quicklinks = models.ManyToManyField(Module, through='Quicklink')
