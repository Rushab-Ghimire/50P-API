import calendar
from collections import defaultdict
import datetime
from core.utils.tf_utils import get_otp
import graphene
from graphene_django.types import DjangoObjectType
from ad.models import ProviderTimeslot
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
from ad.models import *


class ProviderTimeslotType(DjangoObjectType):
    class Meta:
        model = ProviderTimeslot
        fields = "__all__"


class ProviderTimeslotItemType(graphene.ObjectType):
    id = graphene.Int()
    slot = graphene.String()
    full_date_time = graphene.String()


class ProviderTimeslotListType(graphene.ObjectType):
    date = graphene.String()
    slots = graphene.List(ProviderTimeslotItemType)


class ProviderTimeslotDataModelType(graphene.ObjectType):
    data = graphene.List(ProviderTimeslotListType)

    class Meta:
        fields = "data"


class Query(graphene.ObjectType):
    get_provider_time_slots_by_month = graphene.Field(
        ProviderTimeslotDataModelType, date=graphene.String(required=True)
    )

    get_provider_time_slots_by_date = graphene.Field(
        ProviderTimeslotDataModelType, 
        date=graphene.String(required=True), 
        provider_id=graphene.Int(),
        mode=graphene.String(),
    )

    @staticmethod
    def _add_default_timeslot(date_string, session_user):
        org = session_user.get_organization()
        timeList = ["08", "09", "10", "11", "12", "13", "14", "15", "16", "17"]
        for x in timeList:
            date_time = f"{date_string} {x}:00:00+0000"
            print("adding", date_time)
            try:
                date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S%z")
            except ValueError:
                raise ValidationError("Invalid date format. Use 'YYYY-MM-DD'")
            utc_date_time = date_time.astimezone(datetime.timezone.utc)
            time_slot = utc_date_time.time()
            availability_date = utc_date_time.date()
            ProviderTimeslot.objects.create(
                availability_date=availability_date,
                timeslot=time_slot,
                user=session_user,
                organization=org,
            )

    @staticmethod
    def _time_slot_lists(timeslots):
        time_dict = defaultdict(list)
        for timeslot in timeslots:
            date_string = timeslot.availability_date.strftime("%Y-%m-%d")
            full_date_time = f"{date_string}T{timeslot.timeslot}+0000"  # UTC time
            slot_item = {
                "id": timeslot.id,
                "slot": timeslot.timeslot,
                "full_date_time": full_date_time,
            }

            time_dict[date_string].append(slot_item)

        return [{"date": date, "slots": slots} for date, slots in time_dict.items()]

    @login_required
    def resolve_get_provider_time_slots_by_month(self, info, **kwargs):
        session_user = info.context.user
        date = kwargs.get("date")
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Invalid date format. Use 'YYYY-MM-DD'")

        timeslots = (
            ProviderTimeslot.objects.filter(availability_date__month=date.month)
            .filter(user=session_user)
            .order_by("availability_date", "timeslot")
        )

        org = session_user.get_organization()

        data = Query._time_slot_lists(timeslots)

        days_in_month = calendar.monthrange(date.year, date.month)[1]
        dates_in_data = [i["date"] for i in data]
        for day in range(1, days_in_month + 1):
            date_string = date.replace(day=day).strftime("%Y-%m-%d")
            if date_string not in dates_in_data:
                Query._add_default_timeslot(date_string, session_user)
                timeslots = (
                    ProviderTimeslot.objects.filter(availability_date=date_string)
                    .filter(user=session_user)
                    .order_by("timeslot")
                    .prefetch_related("user")
                )
                dataDay = Query._time_slot_lists(timeslots)
                data.append(dataDay[0])

        return ProviderTimeslotDataModelType(data=data)

    @login_required
    def resolve_get_provider_time_slots_by_date(self, info, **kwargs):
        mode = kwargs.get("mode", "doctor")
        provider_id = kwargs.get("provider_id", None)
        if provider_id != None:
            if mode == "lab":
                lab = Lab.objects.get(pk=provider_id)
                print("lab", lab)
                session_user = lab.user if lab.user != None else None
            else:
                doctor = Doctor.objects.get(pk=provider_id)
                print("doctor", doctor)
                session_user = doctor.user if doctor.user != None else None
        else:
            session_user = info.context.user

        date = kwargs.get("date")
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Invalid date format. Use 'YYYY-MM-DD'")

        timeslots = (
            ProviderTimeslot.objects.filter(availability_date=date)
            .filter(user=session_user)
            .order_by("timeslot")
            .prefetch_related("user")
        )

        data = Query._time_slot_lists(timeslots)

        return ProviderTimeslotDataModelType(data=data)


class CreateProviderTimeslot(graphene.Mutation):
    class Arguments:
        date_time = graphene.String(required=True)

    provider_timeslot = graphene.Field(ProviderTimeslotType)

    @login_required
    def mutate(self, info, date_time):
        session_user = info.context.user
        org = session_user.get_organization()

        try:
            date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S%z")
        except ValueError:
            raise ValidationError("Invalid date format. Use 'YYYY-MM-DD'")

        utc_date_time = date_time.astimezone(datetime.timezone.utc)

        time_slot = utc_date_time.time()
        availability_date = utc_date_time.date()

        item, _ = ProviderTimeslot.objects.get_or_create(
            availability_date=availability_date,
            timeslot=time_slot,
            user=session_user,
            organization=org,
        )
        return CreateProviderTimeslot(provider_timeslot=item)

# class UpdateProviderTimeslot(graphene.Mutation):
#     class Arguments:
#         id = graphene.Int(required=True)
#         name = graphene.String()
#         abbr = graphene.String()
#         slug = graphene.String()

#     ProviderTimeslot = graphene.Field(ProviderTimeslotType)

#     def mutate(self, info, id, **kwargs):
#         name = kwargs.get("name")
#         abbr = kwargs.get("abbr")
#         slug = kwargs.get("slug")

#         try:
#             ProviderTimeslot = ProviderTimeslot.objects.get(pk=id)
#         except ProviderTimeslot.DoesNotExist:
#             raise ValidationError("ProviderTimeslot not found")

#         ProviderTimeslot.name = name or ProviderTimeslot.name
#         ProviderTimeslot.abbr = abbr or ProviderTimeslot.abbr
#         if slug:
#             ProviderTimeslot.slug = ProviderTimeslot.generate_slug(slug)

#         ProviderTimeslot.save()
#         return UpdateProviderTimeslot(ProviderTimeslot=ProviderTimeslot)


class DeleteProviderTimeslot(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        try:
            time_slot = ProviderTimeslot.objects.get(pk=id, user=info.context.user)
        except ProviderTimeslot.DoesNotExist:
            raise ValidationError("Time slot not found")

        time_slot.delete()
        return DeleteProviderTimeslot(ok=True)


class Mutation(graphene.ObjectType):
    provider_timeslot_create = CreateProviderTimeslot.Field()
    provider_timeslot_delete = DeleteProviderTimeslot.Field()


provider_timeslot_schema = graphene.Schema(query=Query, mutation=Mutation)
