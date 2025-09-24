import graphene
from graphene_django import DjangoObjectType
from graphene.types.json import JSONString
from salon.models import *
from organization.models import *
import re
from datetime import datetime
from pubsub.consumer import PubSubBroadcaster
from salon.models.setting import get_tax_settings
from core.utils.tf_utils import (
    get_amount_with_currency_code,
    get_customer_file_URL,
    convert_string_to_float,
)
from django.db.models import Q
from graphql_jwt.decorators import login_required
from salon.schemas.selectors import SelectorDataModelType
from salon.schemas.queue import QueueType
import random
from core.utils import google_sheet

class Query(graphene.ObjectType):
    salon_ds = graphene.Field(
        SelectorDataModelType
    )

    def resolve_salon_ds(self, info, **kwargs):
        DS = {}
        totalCount = 1

        d = SelectorDataModelType(totalCount=totalCount, rows=DS)
        return d

class SalonAiBooking(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        contact = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        date_time = graphene.String()
        note = graphene.String()
        org_id = graphene.Int()

    q_item = graphene.Field(QueueType)

    def mutate(self, info, **kwargs):
        org_id = kwargs.get("org_id", -1)
        name = kwargs.get("name", None)
        note = kwargs.get("note", None)
        contact = kwargs.get("contact", None)
        email = kwargs.get("email", "")
        phone = kwargs.get("phone", "")
        date_time = kwargs.get("date_time", None)
        q_date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M%z")

        print("org_id", org_id)
        if org_id == 2:
            row = [name, note, contact, date_time, email, phone]
            print(row)
            google_sheet.add_row(row)
            PubSubBroadcaster.broadcast("common",
                {
                    "event_name": "NEW_NOTIFICATION",
                    "payload": {
                    "id" : "g5",
                    "event_type" : "QUEUE",
                    "userTitle": f"TileFlexAI",
                    "message" : f"Google Sheet for Booking Updated"
                    }
                }
            )
            return SalonAiBooking(q_item={})

        org = Organization.objects.get(pk=org_id)        
        if contact != None:
            valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', contact)
            email = None
            phone = None
            if(valid):
                email = contact
                phone = None
            else:
                phone = contact
                email = None
        else:
            email = kwargs.get("email", "")
            phone = kwargs.get("phone", "")

        [first_name, last_name] = (name.split() + [""])[:2]

        item = None
        if phone == None:
            item = CustomerSalon.objects.filter(email__icontains = email).first()
        else:
            item = CustomerSalon.objects.filter(phone__icontains = phone).first()
        if item == None:
            item = CustomerSalon(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                organization=org,
            )
            item.save()

        q_item = Queue(
            customer = item,
            queue_date_time = q_date_time,
            note = note,
            organization=org,
        )
        q_item.save()

        PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_NOTIFICATION",
            "payload": {
              "id" : q_item.id,
              "event_type" : "QUEUE",
              "userTitle": f"TileFlexAI",
              "message" : f"New Request for Booking"
            }
          }
        )
        return SalonAiBooking(q_item=q_item)

class Mutation(graphene.ObjectType):
    salon_ai_booking = SalonAiBooking.Field()

schema_ai_queue = graphene.Schema(query=Query, mutation=Mutation)
