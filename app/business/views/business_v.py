from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


from rest_framework.decorators import action
from rest_framework.response import Response

from core.base_v import BaseViewSet

from business.models import (
    Entity
)

'''
class BusinessViewSet(BaseViewSet):
    serializer_class = BusinessSerializer
    queryset = Entity.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        return queryset.filter(
            user = self.request.user,
            is_deleted = False
        ).order_by('-title').distinct()


'''
