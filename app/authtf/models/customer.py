from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json
from django.forms.models import model_to_dict
from rest_framework import serializers
from core.base import BaseModel

class Customer(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    business = models.ManyToManyField(
        'business.Entity', blank=True
    )

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['id', 'user',
                  'business',
                  'is_active']
        read_only_fields = ['id']

