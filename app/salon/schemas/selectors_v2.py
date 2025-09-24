import graphene
from graphene_django import DjangoObjectType
from graphene.types.json import JSONString
from salon.models import *
from salon.models.setting import get_tax_settings, get_setting_by_key
from core.utils.tf_utils import (
    get_amount_with_currency_code,
    get_customer_file_URL,
    convert_string_to_float,
    get_file_URL_by_unique_id,
)
from datetime import datetime
from django.db.models import Q
from graphql_jwt.decorators import login_required


class SelectorDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.Field(JSONString)

    class Meta:
        fields = ("totalCount", "rows")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


class OrderDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(OrderType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_order_dataset = graphene.Field(
        SelectorDataModelType,
        order_id=graphene.Int(required=True),
    )

    salon_order = graphene.Field(
        OrderDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )

    @login_required
    def resolve_salon_order(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        org = info.context.user.get_organization()

        qs = Order.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-created_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        d = OrderDataModelType(totalCount=totalCount, rows=qs)
        return d

    def resolve_salon_order_dataset(self, info, order_id, **kwargs):
        DS = {}
        totalCount = 0
        order = (
            Order.objects.select_related("customer", "booking")
            .prefetch_related(
                "booking__bookingservice_set",
                "order_details",
                "payments",
                "organization",
            )
            .get(pk=order_id)
        )
        customer = order.customer
        profile = {
            "name": f"{customer.first_name} {customer.last_name}",
            "email": customer.email,
            "profile_image": get_customer_file_URL(
                customer_id=customer.id,
                key=UserFileKeys.PROFILE_IMAGE,
                type=UserFileTypes.MEDIA,
            ),
            "phone": customer.phone,
            "address": customer.address,
        }

        order_details = order.order_details.all()
        booking_services = (
            order.booking.bookingservice_set.all() if order.booking else []
        )

        services = []
        sub_total = 0
        booking_service_map = {bs.service_id: bs for bs in booking_services}

        if order_details:
            for order_detail in order_details:
                service = Service.objects.filter(pk=order_detail.entity_id).first()
                if service:
                    time_ = service.generate_time_string()
                    ser = {
                        "title": service.title,
                        "ttl": time_,
                        "amount_display": get_amount_with_currency_code(
                            order_detail.subtotal
                        ),
                    }
                    sub_total += order_detail.subtotal

                    if service.id in booking_service_map:
                        bs = booking_service_map[service.id]
                        ser["beautician"] = (
                            bs.beautician.linked_user.first_name
                            if bs.beautician
                            else ""
                        )

                    services.append(ser)

        taxe_rates = get_tax_settings(org_id=order.organization.id)
        taxes = []
        total = sub_total
        for tax in taxe_rates:
            tax_amount = round(
                (convert_string_to_float(tax["value"]) * sub_total) / 100, 2
            )
            total += tax_amount
            taxes.append(
                {
                    "key": tax["key"],
                    "value": f"{tax['value']}%",
                    "amount": tax_amount,
                    "amount_display": get_amount_with_currency_code(tax_amount),
                }
            )

        payment_mode = None
        payment = order.payments.first()
        if payment:
            payment_mode = PaymentMethodSet(payment.payment_method).label

        total = round(total, 2)
        # DO NOT CHANGE THE STRUCTURE . ONLY CHANGE THE DATA
        org_details = {
            key: value
            for key, value in get_setting_by_key(
                [SettingKeys.LOGO, SettingKeys.BUSINESS_PHONE, SettingKeys.PUBLIC_URL]
            ).values_list("key", "value")
        }
        DS = {
            "organization": {
                "name": order.organization.name,
                "details": [
                    {
                        "phone": org_details.get(SettingKeys.BUSINESS_PHONE),
                        "gstin": get_file_URL_by_unique_id(
                            org_details.get(SettingKeys.LOGO), UserFileTypes.MEDIA
                        ),
                        "url": org_details.get(SettingKeys.PUBLIC_URL),
                    },
                ],
            },
            "invoice_date": datetime.strftime(
                order.created_date, "%Y-%m-%d %H:%M:%S%z"
            ),
            "profile": profile,
            "services": services,
            "service_total": {
                "payment_mode": payment_mode,
                "sub_total": sub_total,
                "sub_total_display": get_amount_with_currency_code(sub_total),
                "taxes": taxes,
                "total": total,
                "total_display": get_amount_with_currency_code(total),
            },
        }
        totalCount = 1

        d = SelectorDataModelType(totalCount=totalCount, rows=DS)
        return d


schema_selector_v2 = graphene.Schema(query=Query)
