from datetime import datetime
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ModelV2Manager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(is_deleted=False)


class BaseModelV2(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.SET_NULL,
        null=True,
    )

    objects = ModelV2Manager()

    class Meta:
        abstract = True
