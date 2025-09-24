from django.db import models
from graphene_django import DjangoObjectType

class UIModel(models.Model):
    title = models.TextField(blank=True)
    ui = models.JSONField(blank=True)

    class Meta:
        managed = False

class UIModelType(DjangoObjectType):
  class Meta:
    model = UIModel
    fields = ("title", "ui")