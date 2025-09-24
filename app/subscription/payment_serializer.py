
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class ChargebeeCreateSubscriptionSerializer(serializers.Serializer):
    """Create chargebee subscription."""
    planId = serializers.CharField(max_length=255)

class ChargebeeCustomerUpdateSerializer(serializers.Serializer):
    auto_collection = serializers.BooleanField(required=False)