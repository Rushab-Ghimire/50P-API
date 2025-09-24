"""
Views for the APIs
"""
from rest_framework import (
    viewsets,
    status
)
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from core.authentication import GraphQLJWTAuthentication

class BaseViewSet(viewsets.ModelViewSet):
    authentication_classes = [GraphQLJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted_id' : instance.id}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()



