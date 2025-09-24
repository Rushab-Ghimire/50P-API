from django.db import models
from django.conf import settings
from core.base import BaseModel
from rest_framework import serializers
from organization.models import OrganizationSerializer
from authtf.models.role import RoleSerializer
from salon.models import SettingSerializer, Setting

class UserOrganization(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE)
    role = models.ManyToManyField('authtf.Role')

    class Meta:
        unique_together = ('user', 'organization')
        db_table = "authtf_user_organization"

    def __str__(self):
        return f"{self.user} - {self.organization}"

class OrganizationRoleSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    roles = RoleSerializer(many=True, source='role')

    class Meta:
        model = UserOrganization
        fields = ['organization', 'roles']
        depth = 1


class OrganizationRoleSettingSerializer(OrganizationRoleSerializer):
    settings = serializers.SerializerMethodField()

    class Meta(OrganizationRoleSerializer.Meta):
        fields = OrganizationRoleSerializer.Meta.fields + ["settings"]

    def get_settings(self, obj):
        settings = Setting.objects.filter(organization=obj.organization)
        return SettingSerializer(settings, many=True).data
