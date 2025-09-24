import graphene
from graphene_django import DjangoObjectType
from django.db import models
from datetime import datetime
from graphene.types.json import JSONString
from salon.models import *
from django.db import transaction
from core.utils.tf_utils import get_amount_with_currency_code
from graphql_jwt.decorators import login_required


class CalendarDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.Field(JSONString)

    class Meta:
        fields = ("totalCount", "rows")


class BookingType(DjangoObjectType):
    class Meta:
        model = Booking
        fields = "__all__"


class Query(graphene.ObjectType):
    calendar = graphene.Field(
        CalendarDataModelType,
        inDate=graphene.String(),
    )

    check_occupancy = graphene.Field(
        graphene.Boolean,
        beautician_id=graphene.Int(required=True),
        date_time=graphene.DateTime(),
    )

    salon_booking_by_id = graphene.Field(CalendarDataModelType, id=graphene.Int())

    def resolve_salon_booking_by_id(root, info, id):
        booking = Booking.objects.get(pk=id)
        booking_services = BookingService.objects.filter(booking=booking)

        selected_services = []
        selected_beautician = {}
        for bs in booking_services:
            btcn = {
                "id": bs.beautician.id,
                "name": bs.beautician.linked_user.first_name,
            }
            s = {
                "id": bs.service.id,
                "title": None,
                "time": None,
                "price": None,
                "price_display": None,
            }
            if bs.service:
                time_ = ""
                ttl_hrs = bs.service.ttl_hrs or 0
                ttl_min = bs.service.ttl_min or 0

                if ttl_hrs > 0:
                    time_ = f"{ttl_hrs} {'hrs ' if ttl_hrs > 1 else 'hr '}"

                if ttl_min > 0:
                    time_ += f"{ttl_min} {'mins' if ttl_min > 1 else 'min'}"

                s["time"] = time_ or None
                s["title"] = bs.service.title
                s["price"] = bs.service.sales_price
                s["price_display"] = get_amount_with_currency_code(
                    bs.service.sales_price
                )
            selected_services.append(s)
            selected_beautician[bs.beautician.id] = btcn

        bookingData = {
            "selected_services": selected_services,
            "selected_beautician": list(selected_beautician.values()),
            "selected_date_time": datetime.strftime(
                booking.booking_date_time, "%Y-%m-%d %H:%M:%S%z"
            ),
        }
        totalCount = 1
        d = CalendarDataModelType(totalCount=totalCount, rows=bookingData)
        return d

    def resolve_calendar(self, info, inDate, **kwargs):
        from datetime import datetime

        inDate = datetime.strptime(inDate, "%Y-%m-%d").date()
        # yearMonth = datetime.strptime(inDate, "%Y-%m-%d").date()
        # print("yearMonth", yearMonth)

        bookings = Booking.objects.exclude(status="canceled").filter(
            booking_date_time__year=inDate.year,
            booking_date_time__month=inDate.month,
        ).prefetch_related(
            models.Prefetch("beauticians__linked_user"), models.Prefetch("services")
        )
        events = []
        resource_set = set()

        for booking in bookings:
            beautician = booking.beauticians.first()
            service = booking.services.first()
            resourceId = None
            if beautician:
                resource_set.add((beautician.id, beautician.linked_user.first_name))
                resourceId = beautician.id
                title = (
                    f"{beautician.linked_user.first_name} - {service.title}"
                    if service
                    else beautician.linked_user.first_name
                )
            else:
                title = service.title if service else ""

            events.append(
                {
                    "id": booking.id,
                    "allDay": False,
                    "title": title,
                    "start": booking.checkin_date_time.isoformat(),
                    "end": booking.checkout_date_time.isoformat(),
                    "resourceId": resourceId,
                }
            )

        resource = [{"id": r[0], "name": r[1]} for r in resource_set]

        # events = [
        #     {
        #         "id": 1,
        #         "allDay": False,
        #         "title": "Scott - Hair Cut",  # booking service bata Beauitician ko first name - service ko title
        #         "start": f"${today} 10:30",  # booking ko check in
        #         "end": f"${today} 12:30",  # booking ko checkout
        #         "resourceId": 1,  # beauitician id
        #     },
        #     {
        #         "id": 6,
        #         "allDay": False,
        #         "title": "Anna - Hair Cut",
        #         "start": f"${today} 10:30",
        #         "end": f"${today} 12:30",
        #         "resourceId": 2,
        #     },
        #     {
        #         "id": 16,
        #         "allDay": False,
        #         "title": "Nimesh L - Manicure",
        #         "start": f"${today} 08:30",
        #         "end": f"${today} 9:00",
        #         "resourceId": 3,
        #     },
        #     {
        #         "id": 17,
        #         "allDay": False,
        #         "title": "Nimesh L - Manicure",
        #         "start": f"${today} 11:45",
        #         "end": f"${today} 12:30",
        #         "resourceId": 3,
        #     },
        # ]

        # # All beauticians who have booking on this day
        # resource = [
        #     {"id": 1, "name": "Scott"},
        #     {"id": 2, "name": "Anna"},
        #     {"id": 3, "name": "Nimesh L"},
        # ]

        calendarData = {"events": events, "resource": resource}
        totalCount = len(events)
        d = CalendarDataModelType(totalCount=totalCount, rows=calendarData)
        return d

    def resolve_check_occupancy(self, info, beautician_id, date_time):
        date_time = datetime.strftime(date_time, "%Y-%m-%d %H:%M:%S%z")
        booking = Booking.objects.filter(
            checkin_date_time__lte=date_time,
            checkout_date_time__gte=date_time,
            beauticians__id=beautician_id,
        )
        return bool(booking)


class CreateBooking(graphene.Mutation):
    class Arguments:
        booking_date_time = graphene.String()
        checkin_date_time = graphene.String()
        checkout_date_time = graphene.String()
        customer_id = graphene.Int()
        service_ids = graphene.List(graphene.Int)
        beautician_ids = graphene.List(graphene.Int)
        is_new = graphene.Boolean()
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        phone = graphene.String()

    ok = graphene.Boolean()
    booking = graphene.Field(BookingType)

    @login_required
    def mutate(
        self,
        info,
        booking_date_time,
        checkin_date_time,
        checkout_date_time,
        customer_id,
        service_ids,
        beautician_ids,
        **kwargs,
    ):
        session_user = info.context.user
        org = session_user.get_organization()

        is_new = bool(kwargs.get("is_new"))
        if is_new:
            email = kwargs.get("email")

            customer = CustomerSalon.objects.filter(email=email, organization=org)
            if customer:
                raise Exception("Customer with given email already exist.")

            customer = CustomerSalon.objects.create(
                first_name=kwargs.get("first_name", ""),
                last_name=kwargs.get("last_name", ""),
                email=email,
                phone=kwargs.get("phone", ""),
                organization=org,
            )
        else:
            customer = CustomerSalon.objects.get(id=customer_id, organization=org)

        booking_d = Booking(
            booking_date_time=datetime.strptime(booking_date_time, "%Y-%m-%d %H:%M%z"),
            checkin_date_time=datetime.strptime(checkin_date_time, "%Y-%m-%d %H:%M%z"),
            checkout_date_time=datetime.strptime(
                checkout_date_time, "%Y-%m-%d %H:%M%z"
            ),
            customer=customer,
            organization=org,
            user=session_user,
        )
        booking_d.save()
        transaction.commit()

        for i in range(len(service_ids)):
            service_id = service_ids[i]
            beautician_id = beautician_ids[i]
            service = Service.objects.get(id=service_id)
            beautician = Beautician.objects.get(id=beautician_id)
            booking_service = BookingService(
                booking=booking_d,
                service=service,
                beautician=beautician,
                unit_price=service.sales_price,
                quantity=1,
                subtotal=service.sales_price * 1,
                organization=org,
                user=session_user,
            )
            booking_service.save()

        return CreateBooking(ok=True, booking=booking_d)


class DeleteBooking(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(self, info, id):
        # business = Entity.objects.get(pk=id)
        # business.is_deleted = True
        # business.save()
        return DeleteBooking(ok=True)


class UpdateBooking(graphene.Mutation):
    class Arguments:
        booking_id = graphene.Int()
        booking_date_time = graphene.String()
        checkin_date_time = graphene.String()
        checkout_date_time = graphene.String()
        service_ids = graphene.List(graphene.Int)
        beautician_ids = graphene.List(graphene.Int)

    ok = graphene.Boolean()
    booking = graphene.Field(BookingType)

    @login_required
    def mutate(
        self,
        info,
        booking_date_time,
        checkin_date_time,
        checkout_date_time,
        booking_id,
        service_ids,
        beautician_ids,
        **kwargs,
    ):
        session_user = info.context.user
        org = session_user.get_organization()

        booking = Booking.objects.get(pk=booking_id, organization=org)
        booking.booking_date_time = datetime.strptime(
            booking_date_time, "%Y-%m-%d %H:%M%z"
        )
        booking.checkin_date_time = datetime.strptime(
            checkin_date_time, "%Y-%m-%d %H:%M%z"
        )
        booking.checkout_date_time = datetime.strptime(
            checkout_date_time, "%Y-%m-%d %H:%M%z"
        )
        booking.save()
        booking_services = BookingService.objects.filter(booking=booking)
        booking_services.delete()
        transaction.commit()

        for i in range(len(service_ids)):
            service_id = service_ids[i]
            beautician_id = beautician_ids[i]
            service = Service.objects.get(id=service_id)
            beautician = Beautician.objects.get(id=beautician_id)
            booking_service = BookingService(
                booking=booking,
                service=service,
                beautician=beautician,
                unit_price=service.sales_price,
                quantity=1,
                subtotal=service.sales_price * 1,
                organization=org,
                user=session_user,
            )
            booking_service.save()
        return UpdateBooking(ok=True, booking=booking)


class CreateBookingFromQueue(graphene.Mutation):
    class Arguments:
        booking_date_time = graphene.String()
        checkin_date_time = graphene.String()
        checkout_date_time = graphene.String()
        queue_id = graphene.Int()
        service_ids = graphene.List(graphene.Int)
        beautician_ids = graphene.List(graphene.Int)

    ok = graphene.Boolean()
    booking = graphene.Field(BookingType)

    @login_required
    def mutate(
        self,
        info,
        booking_date_time,
        checkin_date_time,
        checkout_date_time,
        queue_id,
        service_ids,
        beautician_ids,
        **kwargs,
    ):

        session_user = info.context.user
        org = session_user.get_organization()

        queue = Queue.objects.get(id=queue_id, organization=org)
        customer = queue.customer

        booking_d = Booking(
            booking_date_time=datetime.strptime(booking_date_time, "%Y-%m-%d %H:%M%z"),
            checkin_date_time=datetime.strptime(checkin_date_time, "%Y-%m-%d %H:%M%z"),
            checkout_date_time=datetime.strptime(
                checkout_date_time, "%Y-%m-%d %H:%M%z"
            ),
            customer=customer,
            organization=org,
            user=session_user,
        )
        booking_d.save()
        queue.booking = booking_d
        queue.save()
        transaction.commit()

        for i in range(len(service_ids)):
            service_id = service_ids[i]
            beautician_id = beautician_ids[i]
            service = Service.objects.get(id=service_id)
            beautician = Beautician.objects.get(id=beautician_id)
            booking_service = BookingService(
                booking=booking_d,
                service=service,
                beautician=beautician,
                unit_price=service.sales_price,
                quantity=1,
                subtotal=service.sales_price * 1,
                organization=org,
                user=session_user,
            )
            booking_service.save()

        return CreateBookingFromQueue(ok=True, booking=booking_d)


class Mutation(graphene.ObjectType):
    create_booking_from_queue = CreateBookingFromQueue.Field()
    create_booking = CreateBooking.Field()
    delete_booking = DeleteBooking.Field()
    update_booking = UpdateBooking.Field()


schema_calendar = graphene.Schema(query=Query, mutation=Mutation)
