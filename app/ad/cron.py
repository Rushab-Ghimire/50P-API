import datetime
import pytz
from django.db.models import Q
from ad.models import PatientBooking, NotificationStatus
from core.utils.patient_booking_notification import PatientBookingNotification


def patient_booking_reminder():
    timezone = pytz.utc
    now = datetime.datetime.now(timezone)
    notification_time = now + datetime.timedelta(hours=2, minutes=5)

    filter = (
        Q(booking_date_time__range=(now, notification_time))
        & Q(Q(notification_status__flag_reminder=False) | Q(notification_status=None))
    )
    bookings = PatientBooking.objects.filter(filter)

    for booking in bookings:
        try:
            PatientBookingNotification(booking=booking, status="REMINDER").notify_user()

            notification_status, _ = NotificationStatus.objects.get_or_create(booking=booking)
            notification_status.flag_reminder = True
            notification_status.save(update_fields=["flag_reminder"])

        except Exception as e:
            print(str(e))

    print(f"############# Schedular for patient_booking_reminder at {datetime.datetime.now()} #############")
