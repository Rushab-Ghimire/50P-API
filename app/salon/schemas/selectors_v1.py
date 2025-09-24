import graphene
from datetime import datetime
from graphene.types.json import JSONString
from salon.models import *
from core.utils.tf_utils import (
    get_customer_file_URL,
    get_amount_with_currency_code,
    get_user_file_URL,
)
from django.db.models import Q, Sum


class SelectorDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.Field(JSONString)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_customer_dataset = graphene.Field(
        SelectorDataModelType,
        customer_id=graphene.Int(required=True),
    )

    salon_beautician_dataset = graphene.Field(
        SelectorDataModelType,
        beautician_id=graphene.Int(required=True),
    )

    def resolve_salon_customer_dataset(self, info, customer_id, **kwargs):
        DS = {}
        totalCount = 0
        # customer = CustomerSalon.objects.get(pk=customer_id)
        customer = CustomerSalon.objects.prefetch_related(
            "orders",
            "bookings__bookingservice_set__service",
            "bookings__beauticians__linked_user",
            "notes__user",
        ).get(pk=customer_id)
        profile = {
            "profile_image": get_customer_file_URL(
                customer_id=customer.id,
                key=UserFileKeys.PROFILE_IMAGE,
                type=UserFileTypes.MEDIA,
            ),
            "full_name": f"{customer.first_name} {customer.last_name}",
            "email": customer.email,
            "phone": customer.phone,
        }

        invoices = []
        total_sales = 0
        for order in customer.orders.all():
            invoices.append(
                {
                    "invoice_date": order.created_date.strftime("%Y-%b-%d"),
                    "invoice_id": order.id,
                }
            )
            total_sales += order.total

        vouchers = [
            {
                "title": "25% Flat",
                "status": "Sent",
            },
            {
                "title": "5% Flat",
                "status": "Sent",
            },
            {
                "title": "10% On First Visit",
                "status": "Used",
            },
        ]

        bookings = customer.bookings.filter(
            Q(status=BookingStatus.NEW) | Q(status=BookingStatus.COMPLETED)
        )

        appointments = []
        for booking in bookings:
            services = []
            booking_services = booking.bookingservice_set.all()
            if booking_services:
                for bs in booking_services:
                    time_ = ""
                    ttl_hrs = bs.service.ttl_hrs or 0
                    ttl_min = bs.service.ttl_min or 0

                    if ttl_hrs > 0:
                        time_ = f"{ttl_hrs} {'hrs ' if ttl_hrs > 1 else 'hr '}"

                    if ttl_min > 0:
                        time_ += f"{ttl_min} {'mins' if ttl_min > 1 else 'min'}"

                    services.append(f"{time_} - {bs.service.title}")

            beauticians = [
                f"{b.linked_user.first_name} {b.linked_user.last_name}"
                for b in booking.beauticians.all()
            ]

            appointments.append(
                {
                    "date": datetime.strftime(booking.booking_date_time, "%d %B, %Y"),
                    "services": services,
                    "beauticians": beauticians,
                }
            )

        summary = (
            {
                "total_sales": get_amount_with_currency_code(total_sales),
                "all_appointments": customer.bookings.count(),
                "completed_appointments": customer.bookings.filter(
                    status=BookingStatus.COMPLETED
                ).count(),
                "cancelled_appointments": customer.bookings.filter(
                    status=BookingStatus.CANCELED
                ).count(),
                "no_show_appointments": customer.bookings.filter(
                    status=BookingStatus.NOSHOW
                ).count(),
            },
        )

        notes = [
            {"from": f"{note.user.first_name} {note.user.last_name}", "note": note.note}
            for note in customer.notes.all()
        ]

        DS = {
            "profile": profile,
            "invoices": invoices,
            "vouchers": vouchers,
            "appointments": appointments,
            "summary": summary,
            "notes": notes,
        }

        totalCount = 1

        d = SelectorDataModelType(totalCount=totalCount, rows=DS)
        return d

    def resolve_salon_beautician_dataset(self, info, beautician_id, **kwargs):

        beautician = Beautician.objects.get(pk=beautician_id)

        beautician_user = beautician.linked_user

        profile = {
            "user_id": beautician_user.id,
            "profile_image": get_user_file_URL(
                user_id=beautician_user.id,
                key=UserFileKeys.PROFILE_IMAGE,
                type=UserFileTypes.MEDIA,
            ),
            "full_name": f"{beautician_user.first_name} {beautician_user.last_name}",
            "email": beautician_user.email,
            "phone": beautician.phone,
            "address": beautician.address,
        }

        bookings = (
            beautician.booking_set.filter(
                Q(status=BookingStatus.NEW) | Q(status=BookingStatus.COMPLETED)
            )
            .prefetch_related("bookingservice_set__service", "beauticians")
        )

        total_sales = Order.objects.filter(booking__in=bookings).aggregate(total=Sum("total"))["total"] or 0

        appointments = []
        for booking in bookings:
            services = [
                f"{bs.service.generate_time_string()} - {bs.service.title}"
                for bs in booking.bookingservice_set.all()
            ]

            beauticians = [
                f"{b.linked_user.first_name} {b.linked_user.last_name}"
                for b in booking.beauticians.all()
            ]

            appointments.append(
                {
                    "date": booking.booking_date_time.strftime("%d %B, %Y"),
                    "services": services,
                    "beauticians": beauticians,
                }
            )

        summary = (
            {
                "total_sales": get_amount_with_currency_code(total_sales),
                "all_appointments": bookings.count(),
                "completed_appointments": bookings.filter(
                    status=BookingStatus.COMPLETED
                ).count(),
                "cancelled_appointments": bookings.filter(
                    status=BookingStatus.CANCELED
                ).count(),
                "no_show_appointments": bookings.filter(
                    status=BookingStatus.NOSHOW
                ).count(),
            },
        )

        DS = {"profile": profile, "appointments": appointments, "summary": summary}

        totalCount = 1

        d = SelectorDataModelType(totalCount=totalCount, rows=DS)
        return d


schema_selector_v1 = graphene.Schema(query=Query)
