from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json
from django.forms.models import model_to_dict
from core.base import BaseModel

class Package(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
    )
    title = models.CharField(max_length=255)
    description = models.CharField(blank=True, max_length=255)
    icon = models.CharField(blank=True, max_length=255)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"

class DefaultBusinessPackage(BaseModel):
    business = models.ForeignKey("business.Entity", on_delete=models.CASCADE)
    package = models.ForeignKey("Package", on_delete=models.CASCADE)

class OrganizationPackage(BaseModel):
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE)
    package = models.ForeignKey("Package", on_delete=models.CASCADE)
    # add this to User model
    # quicklinks = models.ManyToManyField(Module, through='Quicklink')

