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
    Task, TaskSerializer
)


class TaskViewSet(BaseViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        return queryset.filter(
            user = self.request.user,
            is_deleted = False
        ).order_by('-title').distinct()

