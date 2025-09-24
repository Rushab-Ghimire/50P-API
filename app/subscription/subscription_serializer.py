
from rest_framework import serializers

class CancelSubscriptionSerializer(serializers.Serializer):
    subscriptionId = serializers.CharField(max_length=255)

class UpdateSubscriptionSerializer(serializers.Serializer):
    auto_collection = serializers.BooleanField(required=False)