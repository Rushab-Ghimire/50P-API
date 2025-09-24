from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.response import Response
from core.authentication import GraphQLJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from salon.models import SalonMediaSerializer, SalonDocumentSerializer


class SalonViewSet(viewsets.ViewSet):
    """View for manage recipe APIs."""

    serializer_class = SalonMediaSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [GraphQLJWTAuthentication]

    @action(
        methods=["POST"],
        detail=False,
        url_path="upload-media",
    )
    def salon_upload_media(self, request):
        """Upload a media."""
        serializer = SalonMediaSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        url_path="upload-document",
    )
    def salon_upload_document(self, request):
        """Upload a document."""
        serializer = SalonDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
