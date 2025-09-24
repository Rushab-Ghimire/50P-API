import graphene
from graphene.types.json import JSONString
from salon.models import *
from authtf.models import User
from datetime import date
from core.utils.tf_utils import (
    get_amount_with_currency_code,
)
from django.db.models import Sum, Max, Min, Count
from django.db.models.functions import TruncMonth, TruncYear
from graphql_jwt.decorators import login_required


class SelectorDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.Field(JSONString)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_analytics = graphene.Field(SelectorDataModelType)

    @login_required
    def resolve_salon_analytics(self, info, **kwargs):
        org = info.context.user.get_organization()
        query_monthly = (
            Order.objects.filter(organization=org)
            .filter(created_date__year=date.today().year)
            .annotate(month=TruncMonth("created_date"))
            .values("month")
            .annotate(max_amount=Max("total"), min_amount=Min("total"))
            .order_by("month")
        )

        monthly = [
            {
                "hKey": o.get("month").strftime("%b"),
                "Max": o.get("max_amount"),
                "Min": o.get("min_amount"),
            }
            for o in query_monthly
        ]

        query_yearly = (
            Order.objects.filter(organization=org)
            .filter(created_date__year__gte=(date.today().year - 4))
            .annotate(year=TruncYear("created_date"))
            .values("year")
            .annotate(max_amount=Max("total"), min_amount=Min("total"))
            .order_by("year")
        )

        yearly = [
            {
                "hKey": o.get("year").strftime("%Y"),
                "Max": o.get("max_amount"),
                "Min": o.get("min_amount"),
            }
            for o in query_yearly
        ]

        order_records = Order.objects.filter(organization=org).aggregate(
            total_amount=Sum("total"), count=Count("id")
        )

        leads_count = CustomerSalon.objects.filter(organization=org).count()

        online_signups = User.objects.filter(organizations__in=[org]).count()

        DS = {
            "salesChartData": {
                "monthly": monthly,
                "yearly": yearly,
            },
            "ordersCount": order_records.get("count", 0),
            "leadsCount": leads_count,
            "onlineSignups": online_signups,
            "revenueThisYear": get_amount_with_currency_code(
                order_records.get("total_amount", 0)
            ),
        }

        totalCount = 1

        d = SelectorDataModelType(totalCount=totalCount, rows=DS)
        return d


schema_selector_v3 = graphene.Schema(query=Query)
