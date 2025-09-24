from rest_framework import viewsets
from tf_permissions import IsStaffOrReadOnly
from authtf.models.role import Role, RoleSerializer
from core.authentication import GraphQLJWTAuthentication


class RoleViewSet(viewsets.ModelViewSet):
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [IsStaffOrReadOnly]

    serializer_class = RoleSerializer
    queryset = Role.objects.all()

