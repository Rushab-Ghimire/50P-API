from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


from rest_framework.decorators import action
from rest_framework.response import Response

from core.base_v import BaseViewSet

from authtf.models import (
    Customer,
    CustomerSerializer,
)


class CustomerViewSet(BaseViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        return queryset.filter(
            user = self.request.user,
            is_deleted = False
        ).order_by('-id').distinct()

