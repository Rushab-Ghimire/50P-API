import graphene

from core.utils.email_utils import EmailUtils
from django.core.exceptions import ValidationError
from ad.models import PatientBookingStatuses, PatientBooking, ADAccessCode
from graphql import GraphQLError
from core.utils.patient_booking_notification import PatientBookingNotification


class EmailJSON(graphene.Mutation):
    class Arguments:
        dataset = graphene.String(required=True)
        subject = graphene.String(required=True)

    status = graphene.String()

    def mutate(self, info, dataset, subject, **kwargs):

        # print("dataset", dataset, type(dataset))

        pair_list = dataset.split("||")
        html = "<table>"
        for pair in pair_list:
            key, value = pair.split("::")
            html += f"<tr><td style='width: 100px;'><b>{key} : </b></td><td>{value}</td></tr>"
        html += "</table>"

        # print(html)
        # EmailUtils.html_email(
        #     to_email="rab@askdaysi.com", to_name="AskDaysi", html=html, subject=subject
        # )
        EmailUtils.html_email(
            to_email="feedback@askdaysi.com", to_name="AskDaysi", html=html, subject=subject
        )

        return EmailJSON(status="sent")


class UpdateBookingStatus(graphene.Mutation):
    class Arguments:
        booking_id = graphene.Int(required=True)
        status = graphene.String(required=True)

    status = graphene.String()

    def mutate(self, info, booking_id, status, **kwargs):
        try:
            item = PatientBooking.objects.get(pk=booking_id)
        except PatientBooking.DoesNotExist:
            raise GraphQLError("Booking does not exists")

        status = status.lower()
        if status and status not in PatientBookingStatuses.values:
            raise ValidationError("Invalid status")

        item.status = status
        item.save(update_fields=["status"])

        try:
            PatientBookingNotification(booking=item, update_notification_flag=True).notify_user()
        except Exception as e:
            print(e)

        return UpdateBookingStatus(status=status)

class SendBookingSurvey(graphene.Mutation):
    class Arguments:
        booking_id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, booking_id):
        try:
            item = PatientBooking.objects.get(pk=booking_id)
        except PatientBooking.DoesNotExist:
            raise GraphQLError("Booking does not exists")

        try:
            PatientBookingNotification(booking=item).send_survey()
            success = True
        except Exception as e:
            print(e)
            success = False

        return SendBookingSurvey(ok=success)


class CheckCode(graphene.Mutation):
    class Arguments:
        code = graphene.String(required=True)

    status = graphene.String()

    def mutate(self, info, code, **kwargs):

        if code != "A++DaysiAI":
            raise GraphQLError("Invalid Code")

        return CheckCode(status="ok")


class SaveConcern(graphene.Mutation):
    class Arguments:
        primary_concern = graphene.String()
        hear_about = graphene.String()
        other = graphene.String()

    status = graphene.String()

    def mutate(self, info, **kwargs):

        primary_concern = kwargs.get("primary_concern", "")
        hear_about = kwargs.get("hear_about", "")
        other = kwargs.get("other", "")
        session_user = info.context.user

        if hear_about == "13":
            hear_about = other

        access_code = ADAccessCode.objects.create(
            primary_concern=primary_concern,
            hear_about = hear_about,
            code="one-time-done",
            organization=session_user.get_organization(),
            user=session_user,
        )
        return SaveConcern(status="ok")


class Mutation(graphene.ObjectType):
    email_json = EmailJSON.Field()
    update_ad_booking_status = UpdateBookingStatus.Field()
    check_code = CheckCode.Field()
    save_concern = SaveConcern.Field()
    send_booking_survey = SendBookingSurvey.Field()


schema_ad_micro_tasks_v2 = graphene.Schema(mutation=Mutation)
