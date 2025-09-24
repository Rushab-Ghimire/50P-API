from authtf.models.role import Role
from core.utils import tf_utils
import graphene
from graphene_django import DjangoObjectType
from ad.models import PatientQueue, PatientBooking, PatientBookingStatuses
from organization.models import Organization
from django.conf import settings
from django.db.models import Q
from datetime import datetime
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.apps import apps
from django.db import transaction


class PatientQueueType(DjangoObjectType):
    customer = graphene.Field("authtf.schema_user.UserDetailType")

    class Meta:
        model = PatientQueue
        fields = "__all__"

    def resolve_customer(self, info):
        return self.customer


class PatientQueueDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(PatientQueueType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    patient_queue = graphene.Field(
        PatientQueueDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    patient_queue_by_id = graphene.Field(PatientQueueType, id=graphene.Int())

    @login_required
    def resolve_patient_queue(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = (
                Q(customer__first_name__icontains=search)
                | Q(customer__last_name__icontains=search)
                | Q(customer__email__icontains=search)
                | Q(customer__phone__icontains=search)
            )

        qs = PatientQueue.objects.filter(user=info.context.user)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return PatientQueueDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_patient_queue_by_id(root, info, id):
        return PatientQueue.objects.get(pk=id, user=info.context.user)


class CreatePatientQueue(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        queue_date_time = graphene.String(required=True)
        note = graphene.String()

    ok = graphene.Boolean()
    queue = graphene.Field(PatientQueueType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        if not org:
            raise ValidationError("Organization not found for logged in user.")

        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        phone = kwargs.get("phone")
        email = kwargs.get("email")
        queue_date_time = kwargs.get("queue_date_time")
        note = kwargs.get("note")

        if not email and not phone:
            raise ValidationError("Email or phone is required")

        try:
            queue_date_time = datetime.strptime(queue_date_time, "%Y-%m-%d %H:%M%z")
        except ValueError:
            raise ValidationError("Invalid date format. Use 'YYYY-MM-DD HH:MM±HHMM'")

        if email:
            customer = get_user_model().objects.filter(email=email).first()

        if phone:
            customer = get_user_model().objects.filter(phone=phone).first()

        with transaction.atomic():
            if not customer:
                customer = get_user_model().objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    is_active=True,
                )

                uniq_num = f"{customer.id}{tf_utils.get_otp(3)}"
                customer.set_password(f"Pw$@{uniq_num}")

                if not email:
                    generated_email = f"{customer.first_name.replace(' ', '.').lower()}_{uniq_num}@askdaysi.com"
                    customer.email = generated_email
                    customer.save(update_fields=["email"])

            role = Role.objects.get(identifier="patient")
            UserOrganization = apps.get_model("authtf", "UserOrganization")
            user_organization, created = UserOrganization.objects.get_or_create(
                user=customer, organization=org
            )

            if created or not user_organization.role.filter(id=role.id).exists():
                user_organization.role.add(role)

        q_item = PatientQueue.objects.create(
            customer=customer,
            queue_date_time=queue_date_time,
            note=note,
            organization=org,
            user=session_user,
        )
        return CreatePatientQueue(ok=True, queue=q_item)


class DeletePatientQueue(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        try:
            item = PatientQueue.objects.get(pk=id, user=info.context.user)
        except PatientQueue.DoesNotExist:
            raise Exception("Patient queue does not exist")

        item.is_deleted = True
        item.save()
        return DeletePatientQueue(ok=True)


class UpdatePatientQueue(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        queue_date_time = graphene.String()
        note = graphene.String()

    ok = graphene.Boolean()
    queue = graphene.Field(PatientQueueType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = PatientQueue.objects.get(pk=id, user=info.context.user)
        except PatientQueue.DoesNotExist:
            raise Exception("Patient queue does not exist")

        queue_date_time = kwargs.get("queue_date_time")

        try:
            queue_date_time = datetime.strptime(queue_date_time, "%Y-%m-%d %H:%M%z")
        except ValueError:
            raise ValidationError("Invalid date format. Use 'YYYY-MM-DD HH:MM±HHMM'")

        note = kwargs.get("note")

        item.note = note
        item.queue_date_time = queue_date_time
        item.save(update_fields=["note", "queue_date_time"])
        return UpdatePatientQueue(ok=True, queue=item)


class MoveBookingToQueue(graphene.Mutation):
    class Arguments:
        booking_id = graphene.Int()

    ok = graphene.Boolean()
    queue = graphene.Field(PatientQueueType)

    @login_required
    def mutate(self, info, booking_id):

        try:
            booking = PatientBooking.objects.get(
                pk=booking_id,
                provider=info.context.user,
                status__in=[
                    PatientBookingStatuses.CANCELLED,
                    PatientBookingStatuses.NO_SHOW,
                    PatientBookingStatuses.QUEUED,
                ],
            )
        except PatientBooking.DoesNotExist:
            raise ValidationError("Booking does not exist.")

        queue = PatientQueue.objects.create(
            customer=booking.user,
            queue_date_time=booking.booking_date_time,
            note="Rescheduled",
            booking=booking,
            user=booking.provider,
            organization=booking.organization,
            is_rescheduled=False,
        )

        return MoveBookingToQueue(ok=True, queue=queue)


class Mutation(graphene.ObjectType):
    patient_queue_create = CreatePatientQueue.Field()
    patient_queue_update = UpdatePatientQueue.Field()
    patient_queue_delete = DeletePatientQueue.Field()
    move_to_queue = MoveBookingToQueue.Field()


patient_queue_schema = graphene.Schema(query=Query, mutation=Mutation)
