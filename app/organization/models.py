
from django.apps import apps
from django.db import models, transaction
from core.base import BaseModel
from business.models.entity import BusinessSerializer, Entity
from rest_framework import serializers
from authtf.models.role import Role

class Organization(BaseModel):
    """Organization object."""

    class Meta:
        db_table = "tf_organization"

    name = models.CharField(max_length=255)
    business = models.ForeignKey(
        "business.Entity", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.name


class OrganizationSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    business_id = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(), write_only=True
    )

    class Meta:
        model = Organization
        fields = ["id", "name", "business", "business_id"]
        read_only_fields = ['id']

    def create(self, validated_data):
        """
        Create new organization with selected business.
        Assign current user as an Owner of the organization
        """
        business = validated_data.pop("business_id", None)
        auth_user = self.context["request"].user

        with transaction.atomic():
            organization = Organization.objects.create(**validated_data)

            if business:
                organization.business_id = business.id
                organization.save()

            role = Role.objects.get(identifier="owner")

            UserOrganization = apps.get_model("authtf", "UserOrganization")
            user_organization, created = UserOrganization.objects.get_or_create(user=auth_user, organization=organization)
            user_organization.role.add(role)

            return organization

    def update(self, instance, validated_data):
        """Update organization."""
        business = validated_data.pop('business_id', None)

        if business is not None:
            instance.business_id = business.id

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
