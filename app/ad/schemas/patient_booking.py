import datetime
import graphene
from graphql import GraphQLError
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import PatientBooking, Doctor, PatientQueue, PatientBookingStatuses
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
from core.utils.notification_utils import NotificationUtils
from core.utils.email_utils import EmailUtils
from organization.models import Organization
from authtf.models import Role
from django.apps import apps

class PatientBookingType(DjangoObjectType):
    provider = graphene.Field("ad.schemas.doctor.DoctorType")
    provider_user_id = graphene.Int()
    user_profile_pic = graphene.String()
    user_default_lang = graphene.String()
    provider_default_lang = graphene.String()

    class Meta:
        model = PatientBooking
        fields = "__all__"

    def resolve_provider(self, info):
        return self.provider.doctor_set.first()

    def resolve_provider_user_id(self, info):
        return self.provider.id

    def resolve_user_profile_pic(self, info):
        return self.user.profile_pic()

    def resolve_user_default_lang(self, info):
        return self.user.default_language

    def resolve_provider_default_lang(self, info):
        return self.provider.default_language

    def resolve_user_default_ethnicity(self, info):
        return self.user.default_ethnicity

    def resolve_provider_default_ethnicity(self, info):
        return self.provider.default_ethnicity


class PatientBookingByIdType(DjangoObjectType):
    provider = graphene.Field("ad.schemas.doctor.DoctorType")
    user = graphene.Field("authtf.schema_user.UserDetailType")
    provider_user_id = graphene.Int()
    user_default_lang = graphene.String()
    provider_default_lang = graphene.String()

    class Meta:
        model = PatientBooking
        fields = "__all__"

    def resolve_provider(self, info):
        return self.provider.doctor_set.first()

    def resolve_user(self, info):
        return self.user

    def resolve_provider_user_id(self, info):
        return self.provider.id

    def resolve_user_default_lang(self, info):
        return self.user.default_language

    def resolve_provider_default_lang(self, info):
        return self.provider.default_language

    def resolve_user_default_ethnicity(self, info):
        return self.user.default_ethnicity

    def resolve_provider_default_ethnicity(self, info):
        return self.provider.default_ethnicity


class PatientBookingDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(PatientBookingType)

    class Meta:
        fields = ("totalCount", "rows")

def create_user_for_doctor(doctor):
    email = f"{doctor.id}@askdaysi.com"

    name_parts = doctor.name.split()
    first_name = ""
    last_name = ""

    if name_parts[0].lower() in ["mr.", "dr.", "ms.", "mrs."]:
        name_parts.pop(0)
        first_name = name_parts.pop(0)
    else:
        first_name = name_parts.pop(0)

    for name in name_parts:
        last_name += name + " "

    last_name = last_name.strip()

    password = f"Pw$@{doctor.id}"
    provider = get_user_model().objects.create_user(
        email=email,
        is_active=True,
        is_staff=False,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )

    organization = Organization.objects.filter(business__id=1).first()
    if organization:
        role = Role.objects.get(identifier="doctor")
        UserOrganization = apps.get_model("authtf", "UserOrganization")
        user_organization, _ = UserOrganization.objects.get_or_create(
            user=provider, organization=organization
        )
        user_organization.role.add(role)

    doctor.user = provider
    doctor.save()

    return provider


class Query(graphene.ObjectType):
    patient_booking = graphene.Field(
        PatientBookingDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    patient_booking_by_id = graphene.Field(PatientBookingByIdType, id=graphene.Int())
    my_appointments = graphene.Field(
        PatientBookingDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )

    @login_required
    def resolve_patient_booking(self, info, **kwargs):
        org = info.context.user.get_organization()
        session_user = info.context.user

        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            status_search = search.strip().replace(" ", "")
            if "status=" in status_search:
                status = [s.strip() for s in status_search.split("=")[1].split(",") if s != ""]
                if len(status) > 0:
                    filter = Q(status__in=status)

            else:
                filter = Q(provider__first_name__icontains=search) | Q(
                    user__first_name__icontains=search
                )

        qs = PatientBooking.objects.filter(filter).filter(provider=session_user).filter(organization=org).filter(is_deleted=False)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return PatientBookingDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_patient_booking_by_id(self, info, id):
        try:
            booking = PatientBooking.objects.get(pk=id)
        except PatientBooking.DoesNotExist:
            raise GraphQLError("Booking does not exist")

        return booking


    def resolve_my_appointments(self, info, **kwargs):
        org = info.context.user.get_organization()
        session_user = info.context.user

        search = kwargs.get("search")
        skip = kwargs.get("skip", 0)
        first = kwargs.get("first", 100)

        filter = Q()
        if search:
            filter = Q(provider__first_name__icontains=search) | Q(
                user__first_name__icontains=search
            )

        qs = PatientBooking.objects.filter(filter).filter(organization=org).filter(user=session_user).filter(is_deleted=False)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return PatientBookingDataModelType(totalCount=totalCount, rows=qs)


class CreatePatientBooking(graphene.Mutation):
    class Arguments:
        booking_date_time = graphene.String(required=True)
        provider_id = graphene.Int(required=True)
        insurance_file_uuid = graphene.String()
        report_file_uuid = graphene.String()
        custom_note = graphene.String()
        postal_code = graphene.String()
        insurance_provider = graphene.Int()
        subscription_number = graphene.String()
        member_id = graphene.String()

    patient_booking = graphene.Field(PatientBookingType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user

        booking_date_time = kwargs.get("booking_date_time")
        try:
            booking_date_time = datetime.datetime.strptime(
                booking_date_time, "%Y-%m-%d %H:%M:%S%z"
            )
        except ValueError:
            raise ValidationError(
                "Invalid booking date format. Use 'YYYY-MM-DD HH:MM:SS±HHMM'"
            )

        provider_id = kwargs.get("provider_id")
        try:
            doctor = Doctor.objects.get(pk=provider_id)

            if not doctor.user:
                provider = create_user_for_doctor(doctor)
            else:
                provider = doctor.user

        except Doctor.DoesNotExist:
            raise ValidationError("Provider does not exist")

        postal_code = kwargs.get("postal_code", "")

        insurance_provider = kwargs.get("insurance_provider", -1)
        subscription_number = kwargs.get("subscription_number", "")
        member_id = kwargs.get("member_id", "")

        patient_booking = PatientBooking.objects.create(
            booking_date_time=booking_date_time.astimezone(datetime.timezone.utc),
            provider=provider,
            insurance_file_uuid=kwargs.get("insurance_file_uuid"),
            report_file_uuid=kwargs.get("report_file_uuid"),
            custom_note=kwargs.get("custom_note"),
            status="new",
            postal_code=postal_code,
            organization=session_user.get_organization(),
            user=session_user,
            insurance_provider=insurance_provider,
            subscription_number=subscription_number,
            member_id=member_id,
        )

        NotificationUtils.notify(title = "New Notification", message="New Booking Request", toUser = provider.id, context=info.context, event_type = "BOOKING_REQUEST_PROVIDER", data_string = "booking_id=" + str(patient_booking.id))
        NotificationUtils.notify(title = "New Notification", message="You Placed a New Booking Request", toUser = session_user.id, context=info.context, event_type = "BOOKING_REQUEST_PATIENT", data_string = "booking_id=" + str(patient_booking.id))

        doctor = patient_booking.provider.doctor_set.first()

        html = "<table>"
        html += f"<tr><td style='width: 100px;'><b>Booking # : </b></td><td>{patient_booking.id}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Patient Name : </b></td><td>{patient_booking.user.first_name} {patient_booking.user.last_name}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Booking DateTime : </b></td><td>{patient_booking.booking_date_time}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Postal Code : </b></td><td>{patient_booking.postal_code}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Phone No. : </b></td><td>{patient_booking.user.phone}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Email : </b></td><td>{patient_booking.user.email}</td></tr>"
        html += f"<tr><td colspan='2' style='width: 100px;'>------------------------------------</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Doctor : </b></td><td>{doctor.name} [{doctor.id}]</td></tr>"
        html += "</table>"

        try:
            EmailUtils.html_email(
                to_email="feedback@askdaysi.com", to_name=f"{patient_booking.user.first_name} {patient_booking.user.last_name}", html=html, subject="New Booking Request"
            )
            # EmailUtils.html_email(
            #     to_email="nuru.freelancer@gmail.com", to_name=f"{patient_booking.user.first_name} {patient_booking.user.last_name}", html=html, subject="New Booking Request"
            # )
        except Exception as e:
            print(e)

        return CreatePatientBooking(patient_booking=patient_booking)


class CreatePatientBookingFromQueue(graphene.Mutation):
    class Arguments:
        queue_id = graphene.Int()

    ok = graphene.Boolean()
    patient_booking = graphene.Field(PatientBookingType)

    @login_required
    def mutate(
        self,
        info,
        queue_id
    ):

        session_user = info.context.user

        try:
            queue = PatientQueue.objects.get(id=queue_id, user=session_user, booking=None)
        except PatientQueue.DoesNotExist:
            raise ValidationError("Queue does not exist")

        patient_booking = PatientBooking.objects.create(
            booking_date_time=queue.queue_date_time,
            provider=queue.user,
            insurance_file_uuid=None,
            report_file_uuid=None,
            custom_note=queue.note,
            status="new",
            postal_code=None,
            organization=queue.organization,
            user=queue.customer,
        )

        queue.booking = patient_booking
        queue.is_deleted = True
        queue.save()

        return CreatePatientBookingFromQueue(ok=True, patient_booking=patient_booking)


class UpdatePatientBooking(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        booking_date_time = graphene.String()
        provider_id = graphene.Int()
        insurance_file_uuid = graphene.String()
        report_file_uuid = graphene.String()
        custom_note = graphene.String()
        # status=graphene.String()
        postal_code = graphene.String()
        insurance_provider = graphene.Int()
        subscription_number = graphene.String()
        member_id = graphene.String()

    PatientBooking = graphene.Field(PatientBookingType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = PatientBooking.objects.get(pk=id)
        except PatientBooking.DoesNotExist:
            raise ValidationError("Booking does not exist")

        # provider_id = kwargs.get("provider_id")
        # if provider_id:
        #     try:
        #         doctor = Doctor.objects.get(pk=provider_id)

        #         if not doctor.user:
        #             provider = create_user_for_doctor(doctor)
        #         else:
        #             provider = doctor.user

        #     except Doctor.DoesNotExist:
        #         raise ValidationError("Provider does not exist")

        # status = kwargs.get("status")
        # status = status.lower()
        # if status and status not in PatientBookingStatuses.values:
        #     raise ValidationError("Invalid status")

        booking_date_time = kwargs.get("booking_date_time")
        if booking_date_time:
            try:
                booking_date_time = datetime.datetime.strptime(
                    booking_date_time, "%Y-%m-%d %H:%M:%S%z"
                )
            except ValueError:
                raise ValidationError(
                    "Invalid date format. Use 'YYYY-MM-DD HH:MM:SS±HHMM'"
                )

            item.booking_date_time = booking_date_time.astimezone(datetime.timezone.utc)

        # item.provider = provider if provider_id else item.provider
        item.insurance_file_uuid = kwargs.get(
            "insurance_file_uuid", item.insurance_file_uuid
        )
        item.report_file_uuid = kwargs.get(
            "report_file_uuid", item.report_file_uuid
        )
        item.custom_note = kwargs.get("custom_note", item.custom_note)
        # item.status = status or item.status

        item.postal_code = kwargs.get("postal_code", "")

        item.insurance_provider = kwargs.get("insurance_provider", -1)
        item.subscription_number = kwargs.get("subscription_number", "")
        item.member_id = kwargs.get("member_id", "")

        item.save(
            update_fields=[
                "booking_date_time",
                #"provider",
                "insurance_file_uuid",
                "report_file_uuid",
                "custom_note",
                # "status",
                "postal_code",
                "insurance_provider",
                "subscription_number",
                "member_id",
            ]
        )

        doctor = item.provider.doctor_set.first()
        html = "<table>"
        html += f"<tr><td style='width: 100px;'><b>Booking # : </b></td><td>{item.id}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Patient Name : </b></td><td>{item.user.first_name} {item.user.last_name}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Booking DateTime : </b></td><td>{item.booking_date_time}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Postal Code : </b></td><td>{item.postal_code}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Phone No. : </b></td><td>{item.user.phone}</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Email : </b></td><td>{item.user.email}</td></tr>"
        html += f"<tr><td colspan='2' style='width: 100px;'>------------------------------------</td></tr>"
        html += f"<tr><td style='width: 100px;'><b>Doctor : </b></td><td>{doctor.name} [{doctor.id}]</td></tr>"
        html += "</table>"

        # print("updated...", html)

        try:
            EmailUtils.html_email(
                to_email="feedback@askdaysi.com", to_name=f"{item.user.first_name} {item.user.last_name}", html=html, subject="Booking Request Updated"
            )
            # EmailUtils.html_email(
            #     to_email="nuru.freelancer@gmail.com", to_name=f"{item.user.first_name} {item.user.last_name}", html=html, subject="Booking Request Updated"
            # )
        except Exception as e:
            print(e)

        return UpdatePatientBooking(PatientBooking=item)


class ReschedulePatientBooking(graphene.Mutation):
    class Arguments:
        queue_id = graphene.Int(required=True)
        new_booking_date = graphene.String(required=True)

    ok = graphene.Boolean()
    patient_booking = graphene.Field(PatientBookingType)

    @login_required
    def mutate(self, info, queue_id, new_booking_date):

        session_user = info.context.user

        try:
            booking_date_time = datetime.datetime.strptime(
                new_booking_date, "%Y-%m-%d %H:%M:%S%z"
            )
        except ValueError:
            raise ValidationError(
                "Invalid booking date format. Use 'YYYY-MM-DD HH:MM:SS±HHMM'"
            )

        try:
            queue = PatientQueue.objects.get(id=queue_id, user=session_user)
        except PatientQueue.DoesNotExist:
            raise ValidationError("Queue does not exist")


        booking = queue.booking
        if booking is None:
            raise ValidationError("Booking does not exist for Queue")

        booking.booking_date_time = booking_date_time
        booking.status = PatientBookingStatuses.NEW
        booking.save(update_fields=["booking_date_time", "status"])

        queue.is_rescheduled = True
        queue.is_deleted = True
        queue.queue_date_time = booking_date_time
        queue.save(update_fields=["is_rescheduled", "is_deleted", "queue_date_time"])

        return CreatePatientBookingFromQueue(ok=True, patient_booking=booking)


class DeletePatientBooking(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        item = PatientBooking.objects.get(pk=id)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeletePatientBooking(ok=True)


class Mutation(graphene.ObjectType):
    patient_booking_add = CreatePatientBooking.Field()
    patient_booking_update = UpdatePatientBooking.Field()
    patient_booking_delete = DeletePatientBooking.Field()
    create_patient_booking_from_queue = CreatePatientBookingFromQueue.Field()
    patient_booking_reschedule = ReschedulePatientBooking.Field()


patient_booking_schema = graphene.Schema(query=Query, mutation=Mutation)
