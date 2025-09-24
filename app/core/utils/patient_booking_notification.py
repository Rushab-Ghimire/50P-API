# from django.db import models
import pytz
import datetime
from ad.models import PatientBookingStatuses, NotificationStatus
from .email_utils import EmailUtils
from .tf_utils import send_sms

def generate_display_date_time(booking_date_time, timezone):
    now = datetime.datetime.now(timezone)
    return f"{'Today ' if booking_date_time.date() == now.date() else booking_date_time.strftime('%Y-%m-%d')} at {booking_date_time.strftime('%I:%M%p')}"

class NotifyPatientBookingViaEmail:

    def __init__(self, booking, **kwargs):
        self.booking = booking
        self.kwargs = kwargs

    def notify(self):
        status = self.kwargs.get("status", self.booking.status)
        if status == PatientBookingStatuses.NEW:
            self.status_new()
        elif status == PatientBookingStatuses.CANCELLED:
            self.status_cancelled()
        elif status == PatientBookingStatuses.CONFIRMED:
            self.status_confirmed()
        elif status == "REMINDER":
            self.status_reminder()

    def status_new(self):
        if self.booking.user:
            timezone, address = self.get_doctor_details()
            booking_date_time = self.booking.booking_date_time.astimezone(timezone)

            message = (
                f"{self.booking.user.first_name}, you're scheduled to see {self.booking.provider.first_name}.<br>"
                f"{booking_date_time.strftime('%Y-%m-%d at %I:%M%p')}<br>"
                f"{address}<br>"
                f"Please contact the office {'at '.self.booking.provider.phone+' ' if self.booking.provider.phone else ''} "
                "if you need to cancel or reschedule this appointment.<br>"
                f"Please note: if you do not provide at least 24 hours notice prior to rescheduling, "
                "you will be subject to the office's fee for a missed appointment."
            )

            EmailUtils.html_email(
                to_email=self.booking.user.email,
                to_name=self.booking.user.first_name,
                html=message,
                subject="Appointment Created",
            )

    def status_reminder(self):
        if self.booking.user:
            timezone, address = self.get_doctor_details()
            booking_date_time = self.booking.booking_date_time.astimezone(timezone)
            display_date_time = generate_display_date_time(booking_date_time, timezone)

            message = (
                f"{self.booking.user.first_name}, you're scheduled to see {self.booking.provider.first_name}.<br/>"
                f"{display_date_time}<br/>"
                f"{address}<br/>"
                f"Please contact the office {'at '+self.booking.provider.phone+' ' if self.booking.provider.phone else ''} "
                "if you need to cancel or reschedule this appointment.<br/>"
                f"Please note: if you do not provide at least 24 hours notice prior to rescheduling, "
                "you will be subject to the office's fee for a missed appointment."
            )

            EmailUtils.html_email(
                to_email=self.booking.user.email,
                to_name=self.booking.user.first_name,
                html=message,
                subject="Appointment reminder",
            )

    def status_cancelled(self):
        if self.booking.user:
            timezone, _ = self.get_doctor_details()
            booking_date_time = self.booking.booking_date_time.astimezone(timezone)

            message = (
                f"{self.booking.user.first_name}, your appointment at {booking_date_time.strftime('%Y-%m-%d %H:%M%p')} "
                f"with {self.booking.provider.first_name} has been Cancelled.\n"
                f"Please contact the office {'at '.self.booking.provider.phone+' ' if self.booking.provider.phone else ''}for more information."
            )
            EmailUtils.html_email(
                to_email=self.booking.user.email,
                to_name=self.booking.user.first_name,
                html=message,
                subject="Appointment Cancelled",
            )

    def status_confirmed(self):
        if self.booking.user:
            timezone, _ = self.get_doctor_details()
            booking_date_time = self.booking.booking_date_time.astimezone(timezone)

            message = (
                f"{self.booking.user.first_name}, your appointment at {booking_date_time.strftime('%Y-%m-%d %H:%M%p')} "
                f"with {self.booking.provider.first_name} has been Confirmed.\n"
                f"Please contact the office {'at '+self.booking.provider.phone+' ' if self.booking.provider.phone else ''}for more information."
            )
            EmailUtils.html_email(
                to_email=self.booking.user.email,
                to_name=self.booking.user.first_name,
                html=message,
                subject="Appointment Confirmed",
            )

    def get_doctor_details(self):
        doctor = self.booking.provider.doctor_set.first()
        address = ""
        timezone = pytz.utc
        if doctor:
            address = doctor.address
            if doctor.timezone:
                timezone = pytz.timezone(doctor.timezone)

        return timezone, address


class NotifyPatientBookingViaSMS:
    def __init__(self, booking, **kwargs):
        self.booking = booking
        self.kwargs = kwargs

    def notify(self):
        status = self.kwargs.get("status", self.booking.status)
        if status == PatientBookingStatuses.NEW:
            self.status_new()
        elif status == PatientBookingStatuses.CANCELLED:
            self.status_cancelled()
        elif status == PatientBookingStatuses.CONFIRMED:
            self.status_confirmed()
        elif status == "REMINDER":
            self.status_reminder()

    def status_new(self):
        if self.booking.user:
            timezone, address = self.get_doctor_details()
            booking_date_time = self.booking.booking_date_time.astimezone(timezone)

            message = (
                f"{self.booking.user.first_name}, you're scheduled to see {self.booking.provider.first_name}.\n"
                f"{booking_date_time.strftime('%Y-%m-%d at %I:%M%p')}\n"
                f"{address}\n"
                f"Please contact the office {self.booking.provider.phone+' ' if self.booking.provider.phone else ''}for more information. "
                "If you need to cancel or reschedule this appointment.\n"
                f"Please note: if you do not provide at least 24 hours notice prior to rescheduling, "
                "you will be subject to the office's fee for a missed appointment."
            )

            send_sms(
                to_number=self.booking.user.phone,
                body_text=message,
            )

    def status_reminder(self):
        if self.booking.user:
            timezone, address = self.get_doctor_details()
            booking_date_time = self.booking.booking_date_time.astimezone(timezone)
            display_date_time = generate_display_date_time(booking_date_time, timezone)

            message = (
                f"{self.booking.user.first_name}, you're scheduled to see {self.booking.provider.first_name}.\n"
                f"{display_date_time}\n"
                f"{address}\n"
                f"Please contact the office {'at '+self.booking.provider.phone+' ' if self.booking.provider.phone else ''}if you need to cancel or reschedule this appointment.\n"
                f"Please note: if you do not provide at least 24 hours notice prior to rescheduling, "
                "you will be subject to the office's fee for a missed appointment."
            )

            send_sms(
                to_number=self.booking.user.phone,
                body_text=message,
            )


    def status_cancelled(self):
        if self.booking.user:
            timezone, _ = self.get_doctor_details()
            booking_date_time = self.booking.booking_date_time.astimezone(timezone)

            message = (
                f"{self.booking.user.first_name}, your appointment at {booking_date_time.strftime('%Y-%m-%d %I:%M%p')} "
                f"with {self.booking.provider.first_name} has been Cancelled.\n"
                f"Please contact the office {'at '+self.booking.provider.phone+' ' if self.booking.provider.phone else ''}for more information."
            )
            send_sms(
                to_number=self.booking.user.phone,
                body_text=message,
            )

    def status_confirmed(self):
        if self.booking.user:
            timezone, _ = self.get_doctor_details()
            booking_date_time = self.booking.booking_date_time.astimezone(timezone)

            message = (
                f"{self.booking.user.first_name}, your appointment at {booking_date_time.strftime('%Y-%m-%d %I:%M%p')} "
                f"with {self.booking.provider.first_name} has been Confirmed.\n"
                f"Please contact the office {'at '+self.booking.provider.phone+' ' if self.booking.provider.phone else ''}for more information."
            )
            send_sms(
                to_number=self.booking.user.phone,
                body_text=message,
            )

    def get_doctor_details(self):
        doctor = self.booking.provider.doctor_set.first()
        address = ""
        timezone = pytz.utc
        if doctor:
            address = doctor.address
            if doctor.timezone:
                timezone = pytz.timezone(doctor.timezone)

        return timezone, address


class PatientBookingMessagesViaSMS:
    def __init__(self, booking):
        self.booking = booking

    def send_survey_form(self):
        if self.booking.user:

            survey_link = "https://forms.gle/UXmhcKuZe25W2B6P8"
            message = (
                f"{self.booking.user.first_name}!\n,"
                f"{self.booking.provider.first_name} would like you to complete these forms. Please follow the link below.\n"
                f"{survey_link}\n"
                f"Please contact the office {'at '+self.booking.provider.phone+' ' if self.booking.provider.phone else ''}for more information."
            )

            send_sms(
                to_number=self.booking.user.phone,
                body_text=message,
            )

    def get_doctor_details(self):
        doctor = self.booking.provider.doctor_set.first()
        address = ""
        timezone = pytz.utc
        if doctor:
            address = doctor.address
            if doctor.timezone:
                timezone = pytz.timezone(doctor.timezone)

        return timezone, address

class PatientBookingMessagesViaEmail:
    def __init__(self, booking):
        self.booking = booking

    def send_survey_form(self):
        if self.booking.user:
            survey_link = "https://forms.gle/UXmhcKuZe25W2B6P8"
            message = (
                f"{self.booking.user.first_name}!<br>,"
                f"{self.booking.provider.first_name} would like you to complete these forms. Please follow the link below.<br>"
                f"{survey_link}<br>"
                f"Please contact the office {'at '+self.booking.provider.phone+' ' if self.booking.provider.phone else ''}for more information. "
            )

            EmailUtils.html_email(
                to_email=self.booking.user.email,
                to_name=self.booking.user.first_name,
                html=message,
                subject="Survey request",
            )

    def get_doctor_details(self):
        doctor = self.booking.provider.doctor_set.first()
        address = ""
        timezone = pytz.utc
        if doctor:
            address = doctor.address
            if doctor.timezone:
                timezone = pytz.timezone(doctor.timezone)

        return timezone, address


class PatientBookingNotification:
    def __init__(self, booking, type=None, **kwargs):
        self.booking = booking

        if type is None:
            type = ["sms", "email"]
        elif isinstance(type, str):
            type = [type]

        self.type = type
        self.kwargs = kwargs

    def notify_user(self):
        if "sms" in self.type:
            NotifyPatientBookingViaSMS(self.booking, **self.kwargs).notify()
        if "email" in self.type:
            NotifyPatientBookingViaEmail(self.booking, **self.kwargs).notify()

        if self.kwargs.get("update_notification_flag", False):
            notification_status = self.booking.notification_status.first()
            if not notification_status:
                notification_status = NotificationStatus.objects.create(
                    booking=self.booking
                )

            if self.booking.status == PatientBookingStatuses.NEW:
                notification_status.flag_new = True
            elif self.booking.status == PatientBookingStatuses.CANCELLED:
                notification_status.flag_cancelled = True
            elif self.booking.status == PatientBookingStatuses.CONFIRMED:
                notification_status.flag_confirmed = True

            notification_status.save()

    def send_survey(self):
        if "sms" in self.type:
            PatientBookingMessagesViaSMS(self.booking).send_survey_form()
        if "email" in self.type:
            PatientBookingMessagesViaEmail(self.booking).send_survey_form()
