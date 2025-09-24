from rest_framework import viewsets
from rest_framework import permissions
from organization.models import Organization, OrganizationSerializer
from core.authentication import GraphQLJWTAuthentication

class OrganizationViewSet(viewsets.ModelViewSet):
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
