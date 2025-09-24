import graphene
from authtf.models import Feedback
from salon.models import Pos, EntityType
from salon.models import *
from graphene.types.json import JSONString
from core.utils.tf_utils import (
    generate_salon_order_code,
    generate_salon_receipt_number,
    get_unique_key,
    send_sms,
)
from django.db import transaction
from graphql_jwt.decorators import login_required


class MicroTaskDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.Field(JSONString)

    class Meta:
        fields = ("totalCount", "rows")


class SalonUpdateBookingServiceStatus(graphene.Mutation):
    class Arguments:
        status = graphene.String(required=True)
        booking_service_id = graphene.Int()
        pos_id = graphene.Int()

    status = graphene.String()
    booking_service_id = graphene.Int()
    pos_id = graphene.Int()

    def mutate(self, info, **kwargs):
        booking_service_id = kwargs.get("booking_service_id")
        status = kwargs.get("status")
        pos_id = kwargs.get("pos_id")
        # update booking-service to status. query status from status table
        booking_service = BookingService.objects.get(pk=booking_service_id)
        if status == "START":
            status = "running"
        status = SessionStatus.objects.get(title=status.lower())
        if pos_id:
            Pos.objects.get(pk=pos_id)
            booking_service.pos_id = pos_id

        booking_service.status = status
        booking_service.save()
        return SalonUpdateBookingServiceStatus(
            booking_service_id=booking_service_id, status=status, pos_id=pos_id
        )


class SalonCompleteOrder(graphene.Mutation):
    class Arguments:
        payment_mode = graphene.Int(required=True)
        booking_id = graphene.Int()

    payment_mode = graphene.String()
    booking_id = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        payment_mode = kwargs.get("payment_mode")
        booking_id = kwargs.get("booking_id")

        org = info.context.user.get_organization()

        # create Order & Order Detail
        booking = Booking.objects.get(pk=booking_id)
        booking_services = BookingService.objects.filter(booking_id=booking_id)
        entity_type = EntityType.objects.get(title="Service")
        customer = booking.customer

        with transaction.atomic():
            total = 0
            order = Order.objects.create(
                order_code=generate_salon_order_code(),
                receipt_number=generate_salon_receipt_number(),
                total=total,
                customer=customer,
                booking=booking,
                organization=org,
            )

            order_details = list()
            for bs in booking_services:
                total += bs.subtotal
                order_details.append(
                    OrderDetail(
                        price=bs.unit_price,
                        quantity=bs.quantity,
                        subtotal=bs.subtotal,
                        entity_id=bs.service.id,
                        entity_type=entity_type,
                        order=order,
                    )
                )

            OrderDetail.objects.bulk_create(order_details)

            order.total = total
            order.save(update_fields=["total"])

            payment = Payment.objects.create(
                payment_method=payment_mode,
                amount=total,
                order=order,
            )
            payment.save()

            booking.status = BookingStatus.COMPLETED
            booking.save(update_fields=["status"])

            feedback = Feedback.objects.create(
                unique_id=get_unique_key(),
                order=order,
                rating=-1,
                comment=None,
                organization=org,
            )
            try:
                send_sms(
                    customer.phone,
                    f"Thanks for letting us serve you.\n"
                    f"For feedback - "
                    f"{feedback.get_link()}",
                )
            except Exception as e:
                print(e)

        return SalonCompleteOrder(payment_mode=payment_mode, booking_id=booking_id)


class SalonCancelBooking(graphene.Mutation):
    class Arguments:
        booking_id = graphene.Int()

    booking_id = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        org = info.context.user.get_organization()
        booking_id = kwargs.get("booking_id", None)
        if not booking_id:
            raise Exception("Booking Id is required.")
        booking = Booking.objects.get(organization=org, id=booking_id)
        booking.status = BookingStatus.CANCELED
        booking.save()
        return SalonCancelBooking(booking_id=booking_id)


class Mutation(graphene.ObjectType):
    salon_update_booking_service_status = SalonUpdateBookingServiceStatus.Field()
    salon_complete_order = SalonCompleteOrder.Field()
    salon_cancel_booking = SalonCancelBooking.Field()


schema_micro_tasks = graphene.Schema(mutation=Mutation)
