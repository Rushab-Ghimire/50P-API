from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework.decorators import action
from rest_framework.response import Response

from core.base_v import BaseViewSet

from card.models import (
    ContextCard, ContextCardSerializer,
)

class ContextCardViewSet(BaseViewSet):
    serializer_class = ContextCardSerializer
    queryset = ContextCard.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        return queryset.filter(
            user = self.request.user,
            is_deleted = False
        ).order_by('-title').distinct()

