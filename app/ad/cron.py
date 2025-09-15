import datetime
import pytz
from django.db.models import Q


def my_scheduler():
    print(f"############# Schedular at {datetime.datetime.now()} #############")
